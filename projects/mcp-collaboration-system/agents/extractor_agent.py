"""
Extractor Agent for MCP-S (Multi-Agent Collaboration System)
============================================================

Role: Content Extraction Agent
Skills: epub-parser, pdf-parser, text-extractor, structure-parser
Model: opencode/minimax-m2.5-free

This agent handles:
- EPUB file parsing and TOC extraction
- PDF file parsing and text extraction
- Chapter content extraction
- Structured data return
"""

import asyncio
import json
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pathlib import Path
import tempfile
import os

# Try to import PDF libraries
try:
    import fitz as pymupdf_lib

    PYMUPDF_AVAILABLE = True
except ImportError:
    pymupdf_lib = None
    PYMUPDF_AVAILABLE = False

PYMUPDF_MODULE = pymupdf_lib


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExtractionFormat(Enum):
    EPUB = "epub"
    PDF = "pdf"
    TEXT = "text"
    STRUCTURED = "structured"


@dataclass
class ExtractionResult:
    success: bool
    format: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    toc: List[Dict[str, Any]] = field(default_factory=list)
    content: str = ""
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractorConfig:
    role_id: str = "extractor"
    role_name: str = "内容提取 Agent"
    agent_type: str = "opencode"
    model: str = "opencode/minimax-m2.5-free"
    skills: List[str] = field(
        default_factory=lambda: [
            "epub-parser",
            "pdf-parser",
            "text-extractor",
            "structure-parser",
        ]
    )
    max_file_size_mb: int = 100
    timeout_seconds: int = 300


class EPUBParser:
    """
    EPUB Parser Skill
    Extracts metadata, TOC, and content from EPUB files
    """

    NS = {
        "opf": "http://www.idpf.org/2007/opf",
        "dc": "http://purl.org/dc/elements/1.1/",
        "container": "urn:oasis:names:tc:opendocument:xmlns:container",
    }

    def __init__(self):
        self.name = "epub-parser"
        self.description = "Parse EPUB files, extract metadata, TOC, and content"

    async def parse(self, file_path: str) -> ExtractionResult:
        """Parse an EPUB file and return structured data"""
        try:
            result = ExtractionResult(success=False, format="epub")

            if not Path(file_path).exists():
                result.error = f"File not found: {file_path}"
                return result

            # Extract EPUB (it's a ZIP archive)
            metadata, toc, chapters = await self._extract_epub(file_path)

            result.success = True
            result.metadata = metadata
            result.toc = toc
            result.chapters = chapters
            result.content = "\n\n".join([ch.get("content", "") for ch in chapters])
            result.stats = {
                "total_chapters": len(chapters),
                "toc_entries": len(toc),
                "content_length": len(result.content),
            }

            return result

        except Exception as e:
            return ExtractionResult(success=False, format="epub", error=str(e))

    async def _extract_epub(self, file_path: str) -> tuple:
        """Extract content from EPUB file"""
        metadata = {}
        toc = []
        chapters = []

        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract EPUB
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(tmpdir)

            # Find container.xml
            container_path = Path(tmpdir) / "META-INF" / "container.xml"
            if not container_path.exists():
                raise ValueError("Invalid EPUB: container.xml not found")

            # Parse container.xml to find OPF file
            tree = ET.parse(container_path)
            root = tree.getroot()
            rootfile = root.find(
                ".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile"
            )

            if rootfile is None:
                raise ValueError("Invalid EPUB: rootfile not found in container.xml")

            full_path = rootfile.get("full-path")
            if not full_path:
                raise ValueError("Invalid EPUB: rootfile has no full-path attribute")

            opf_path = Path(tmpdir) / full_path
            opf_dir = opf_path.parent

            # Parse OPF file
            opf_tree = ET.parse(opf_path)
            opf_root = opf_tree.getroot()

            # Extract metadata
            metadata = self._extract_metadata(opf_root)

            # Build manifest (file id -> href mapping)
            manifest = {}
            for item in opf_root.findall(".//{http://www.idpf.org/2007/opf}item"):
                item_id = item.get("id")
                href = item.get("href")
                media_type = item.get("media-type")
                if item_id and href:
                    manifest[item_id] = {
                        "href": href,
                        "media_type": media_type,
                        "path": opf_dir / href,
                    }

            # Extract TOC from nav.xhtml or NCX
            toc = await self._extract_toc(opf_root, manifest, tmpdir, opf_dir)

            # Extract spine order
            spine_items = []
            for itemref in opf_root.findall(".//{http://www.idpf.org/2007/opf}itemref"):
                idref = itemref.get("idref")
                if idref in manifest:
                    spine_items.append(manifest[idref])

            # Extract chapter content
            for idx, item in enumerate(spine_items):
                if item["media_type"] in ["application/xhtml+xml", "text/html"]:
                    content = await self._extract_html_content(str(item["path"]))
                    chapters.append(
                        {
                            "index": idx,
                            "title": self._extract_title_from_html(content)
                            or f"Chapter {idx + 1}",
                            "href": item["href"],
                            "content": content,
                        }
                    )

        return metadata, toc, chapters

    def _extract_metadata(self, opf_root) -> Dict[str, Any]:
        """Extract metadata from OPF file"""
        metadata = {}

        # Namespace mappings
        ns = {
            "opf": "http://www.idpf.org/2007/opf",
            "dc": "http://purl.org/dc/elements/1.1/",
        }

        # Try to find metadata element
        metadata_elem = opf_root.find(f".//opf:metadata", ns)
        if metadata_elem is None:
            metadata_elem = opf_root.find(".//{http://www.idpf.org/2007/opf}metadata")
        if metadata_elem is None:
            metadata_elem = opf_root.find("metadata")

        if metadata_elem is not None:
            # Extract DC elements
            for tag_name in [
                "title",
                "creator",
                "language",
                "subject",
                "description",
                "publisher",
            ]:
                # Try with namespace
                elem = metadata_elem.find(f".//dc:{tag_name}", ns)
                if elem is None:
                    elem = metadata_elem.find(
                        f".//{{http://purl.org/dc/elements/1.1/}}{tag_name}"
                    )
                if elem is None:
                    elem = metadata_elem.find(tag_name)

                if elem is not None and elem.text:
                    metadata[tag_name] = elem.text.strip()

            # Extract opf:meta elements
            for meta in metadata_elem.findall(".//{http://www.idpf.org/2007/opf}meta"):
                name = meta.get("name")
                content = meta.get("content")
                if name and content:
                    metadata[name] = content

        return metadata

    async def _extract_toc(
        self, opf_root, manifest, tmpdir, opf_dir
    ) -> List[Dict[str, Any]]:
        """Extract table of contents"""
        toc = []

        # Try to find nav.xhtml (EPUB 3)
        nav_item = None
        for item_id, item_data in manifest.items():
            if item_data["href"].endswith("nav.xhtml") or item_data["href"].endswith(
                "nav.html"
            ):
                nav_item = item_data
                break

        if nav_item:
            toc = await self._extract_nav_toc(str(nav_item["path"]))
        else:
            # Try NCX (EPUB 2)
            ncx_item = None
            for item_id, item_data in manifest.items():
                if item_data["media_type"] == "application/x-dtbncx+xml":
                    ncx_item = item_data
                    break

            if ncx_item:
                toc = self._extract_ncx_toc(str(ncx_item["path"]))

        return toc

    async def _extract_nav_toc(self, nav_path: str) -> List[Dict[str, Any]]:
        """Extract TOC from nav.xhtml"""
        toc = []
        try:
            tree = ET.parse(nav_path)
            root = tree.getroot()

            # Find nav element with epub:type="toc"
            navs = root.findall(".//{http://www.w3.org/1999/xhtml}nav")
            for nav in navs:
                epub_toc = nav.get("{http://www.idpf.org/2007/opf}type")
                if epub_toc == "toc" or nav.get("id") == "toc":
                    toc = self._parse_nav_list(nav)
                    break
        except Exception:
            pass
        return toc

    def _parse_nav_list(self, nav_elem) -> List[Dict[str, Any]]:
        """Parse nav list elements"""
        toc = []
        ol = nav_elem.find(".//{http://www.w3.org/1999/xhtml}ol")
        if ol is not None:
            for idx, li in enumerate(ol.findall("{http://www.w3.org/1999/xhtml}li")):
                a = li.find(".//{http://www.w3.org/1999/xhtml}a")
                if a is not None:
                    item = {
                        "index": idx,
                        "label": a.text.strip() if a.text else "",
                        "href": a.get("href", ""),
                    }
                    # Check for nested list
                    nested_ol = li.find("./{http://www.w3.org/1999/xhtml}ol")
                    if nested_ol is not None:
                        item["subitems"] = self._parse_nav_list_from_ol(nested_ol)
                    toc.append(item)
        return toc

    def _parse_nav_list_from_ol(self, ol) -> List[Dict[str, Any]]:
        """Parse nested nav list from ol element"""
        items = []
        for idx, li in enumerate(ol.findall("{http://www.w3.org/1999/xhtml}li")):
            a = li.find(".//{http://www.w3.org/1999/xhtml}a")
            if a is not None:
                item = {
                    "index": idx,
                    "label": a.text.strip() if a.text else "",
                    "href": a.get("href", ""),
                }
                nested_ol = li.find("./{http://www.w3.org/1999/xhtml}ol")
                if nested_ol is not None:
                    item["subitems"] = self._parse_nav_list_from_ol(nested_ol)
                items.append(item)
        return items

    def _extract_ncx_toc(self, ncx_path: str) -> List[Dict[str, Any]]:
        """Extract TOC from NCX file (EPUB 2)"""
        toc = []
        try:
            tree = ET.parse(ncx_path)
            root = tree.getroot()

            nav_map = root.find(".//{http://www.daisy.org/z3986/2005/ncx/}navMap")
            if nav_map is not None:
                toc = self._parse_ncx_navpoints(nav_map)
        except Exception:
            pass
        return toc

    def _parse_ncx_navpoints(self, nav_map, depth=0) -> List[Dict[str, Any]]:
        """Parse NCX navPoints recursively"""
        toc = []
        for idx, nav_point in enumerate(
            nav_map.findall("{http://www.daisy.org/z3986/2005/ncx/}navPoint")
        ):
            nav_label = nav_point.find("{http://www.daisy.org/z3986/2005/ncx/}navLabel")
            text_elem = (
                nav_label.find("{http://www.daisy.org/z3986/2005/ncx/}text")
                if nav_label
                else None
            )
            content = nav_point.find("{http://www.daisy.org/z3986/2005/ncx/}content")

            item = {
                "index": idx,
                "label": text_elem.text.strip()
                if text_elem is not None and text_elem.text
                else "",
                "href": content.get("src", "") if content is not None else "",
                "depth": depth,
            }

            nested = nav_point.find("{http://www.daisy.org/z3986/2005/ncx/}navPoint")
            if nested is not None:
                item["subitems"] = self._parse_ncx_navpoints(nav_point, depth + 1)

            toc.append(item)
        return toc

    async def _extract_html_content(self, html_path: str) -> str:
        """Extract text content from HTML/XHTML file"""
        try:
            tree = ET.parse(html_path)
            root = tree.getroot()

            # Remove script and style elements
            for elem in root.iter():
                if elem.tag in ["script", "style", "head"]:
                    continue
                if elem.text and elem.tag in [
                    "p",
                    "div",
                    "span",
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "li",
                ]:
                    text = elem.text.strip()
                    if text:
                        yield_text = text
                if elem.tail and elem.tail.strip():
                    pass

            # Simple text extraction
            text_parts = []
            for elem in root.iter():
                if elem.tag in ["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"]:
                    text = "".join(elem.itertext()).strip()
                    if text:
                        text_parts.append(text)

            return "\n\n".join(text_parts)
        except Exception:
            return ""

    def _extract_title_from_html(self, content: str) -> Optional[str]:
        """Extract title from HTML content"""
        first_line = content.split("\n")[0] if content else ""
        return first_line[:200] if first_line else None


class PDFParser:
    """
    PDF Parser Skill
    Extracts text content and metadata from PDF files
    """

    def __init__(self):
        self.name = "pdf-parser"
        self.description = "Parse PDF files, extract text content and metadata"

    async def parse(self, file_path: str) -> ExtractionResult:
        """Parse a PDF file and return structured data"""
        result = ExtractionResult(success=False, format="pdf")

        if not Path(file_path).exists():
            result.error = f"File not found: {file_path}"
            return result

        if not PYMUPDF_AVAILABLE:
            result.error = (
                "PyMuPDF (fitz) is not installed. Install with: pip install pymupdf"
            )
            return result

        try:
            if PYMUPDF_MODULE is None:
                result.error = "PyMuPDF not available"
                return result
            doc = PYMUPDF_MODULE.open(file_path)

            # Extract metadata
            result.metadata = self._extract_metadata(doc)

            # Extract TOC if available
            result.toc = self._extract_toc(doc)

            # Extract content by pages
            chapters = []
            current_chapter = {"title": "Chapter 1", "start_page": 1, "content": ""}

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()

                # Simple chapter detection (could be improved)
                if text.strip():
                    if (
                        len(current_chapter["content"]) > 5000
                    ):  # New chapter every 5000 chars
                        chapters.append(current_chapter)
                        current_chapter = {
                            "title": f"Page {page_num + 1}",
                            "start_page": page_num + 1,
                            "content": "",
                        }

                    current_chapter["content"] += (
                        f"\n\n--- Page {page_num + 1} ---\n\n{text}"
                    )

            if current_chapter["content"]:
                chapters.append(current_chapter)

            result.chapters = chapters
            result.content = "\n\n".join([ch.get("content", "") for ch in chapters])
            result.success = True

            result.stats = {
                "total_pages": len(doc),
                "total_chapters": len(chapters),
                "content_length": len(result.content),
            }

            doc.close()
            return result

        except Exception as e:
            result.error = str(e)
            return result

    def _extract_metadata(self, doc) -> Dict[str, Any]:
        """Extract metadata from PDF document"""
        metadata = {}

        try:
            doc_metadata = doc.metadata
            if doc_metadata:
                metadata = {
                    "title": doc_metadata.get("title", ""),
                    "author": doc_metadata.get("author", ""),
                    "subject": doc_metadata.get("subject", ""),
                    "creator": doc_metadata.get("creator", ""),
                    "producer": doc_metadata.get("producer", ""),
                    "creation_date": doc_metadata.get("creationDate", ""),
                    "modification_date": doc_metadata.get("modDate", ""),
                }
        except Exception:
            pass

        return {k: v for k, v in metadata.items() if v}

    def _extract_toc(self, doc) -> List[Dict[str, Any]]:
        """Extract table of contents from PDF"""
        toc = []

        try:
            toc_items = doc.get_toc()
            if toc_items:
                for idx, item in enumerate(toc_items):
                    # TOC item format: [level, title, page, ...]
                    toc_entry = {
                        "index": idx,
                        "level": item[0] if len(item) > 0 else 1,
                        "label": item[1] if len(item) > 1 else "",
                        "page": item[2] if len(item) > 2 else 0,
                    }
                    toc.append(toc_entry)
        except Exception:
            pass

        return toc


class TextExtractor:
    """
    Text Extractor Skill
    Extracts clean text content from various formats
    """

    def __init__(self):
        self.name = "text-extractor"
        self.description = "Extract clean text content from structured documents"

    async def extract(self, result: ExtractionResult, clean: bool = True) -> str:
        """Extract and optionally clean text from extraction result"""
        text = result.content

        if clean:
            text = self._clean_text(text)

        return text

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        import re

        # Remove excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        # Remove common noise patterns
        text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", text)

        return text.strip()

    async def extract_chapters(self, result: ExtractionResult) -> List[str]:
        """Extract chapter contents as list"""
        return [ch.get("content", "") for ch in result.chapters]


class StructureParser:
    """
    Structure Parser Skill
    Parses document structure and returns hierarchical data
    """

    def __init__(self):
        self.name = "structure-parser"
        self.description = "Parse document structure into hierarchical data"

    async def parse(self, result: ExtractionResult) -> Dict[str, Any]:
        """Parse extraction result into structured format"""
        structure = {
            "metadata": result.metadata,
            "table_of_contents": self._build_toc_tree(result.toc),
            "chapters": [],
            "statistics": result.stats,
        }

        for ch in result.chapters:
            chapter_struct = {
                "index": ch.get("index", 0),
                "title": ch.get("title", ""),
                "sections": self._extract_sections(ch.get("content", "")),
                "word_count": len(ch.get("content", "").split()),
            }
            structure["chapters"].append(chapter_struct)

        return structure

    def _build_toc_tree(self, toc: List[Dict]) -> Dict[str, Any]:
        """Build hierarchical TOC tree from flat list"""
        root = {"label": "Root", "children": []}
        stack = [(0, root)]  # (level, node)

        for item in toc:
            level = item.get("depth", item.get("level", 1))
            node = {
                "label": item.get("label", ""),
                "href": item.get("href", ""),
                "children": [],
            }

            # Find parent - pop items at same or deeper level
            while stack and stack[-1][0] >= level:
                stack.pop()

            # Ensure stack is not empty
            if not stack:
                stack.append((0, root))

            stack[-1][1]["children"].append(node)
            stack.append((level, node))

        return root

    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract sections from chapter content"""
        import re

        sections = []
        lines = content.split("\n")
        current_section = {"title": "Introduction", "content": ""}

        for line in lines:
            # Detect section headers
            if re.match(r"^#{1,6}\s+(.+)", line.strip()):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {
                    "title": line.strip().lstrip("#").strip(),
                    "content": "",
                }
            elif re.match(r"^Chapter\s+\d+", line.strip(), re.IGNORECASE):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"title": line.strip(), "content": ""}
            else:
                current_section["content"] += line + "\n"

        if current_section["content"]:
            sections.append(current_section)

        return sections


class ExtractorAgent:
    """
    Main Extractor Agent
    Integrates all parsing skills and provides unified interface
    """

    def __init__(self, config: Optional[ExtractorConfig] = None):
        self.config = config or ExtractorConfig()

        # Initialize skills
        self.epub_parser = EPUBParser()
        self.pdf_parser = PDFParser()
        self.text_extractor = TextExtractor()
        self.structure_parser = StructureParser()

        # Role metadata
        self.role_id = self.config.role_id
        self.role_name = self.config.role_name
        self.agent_type = self.config.agent_type
        self.model = self.config.model
        self.skills = self.config.skills

    async def process(
        self, file_path: str, file_format: Optional[str] = None
    ) -> ExtractionResult:
        """
        Process a file and extract content

        Args:
            file_path: Path to the file to process
            file_format: Optional format hint (epub/pdf). Auto-detected if not provided.

        Returns:
            ExtractionResult with extracted content
        """
        # Auto-detect format from extension
        if file_format is None:
            ext = Path(file_path).suffix.lower()
            if ext == ".epub":
                file_format = "epub"
            elif ext == ".pdf":
                file_format = "pdf"
            else:
                return ExtractionResult(
                    success=False,
                    format="unknown",
                    error=f"Unknown file format: {ext}. Please specify epub or pdf.",
                )

        if file_format == "epub":
            return await self.epub_parser.parse(file_path)
        elif file_format == "pdf":
            return await self.pdf_parser.parse(file_path)
        else:
            return ExtractionResult(
                success=False,
                format=file_format,
                error=f"Unsupported format: {file_format}",
            )

    async def extract_text(self, result: ExtractionResult, clean: bool = True) -> str:
        """Extract clean text from result"""
        return await self.text_extractor.extract(result, clean)

    async def get_structure(self, result: ExtractionResult) -> Dict[str, Any]:
        """Get structured representation of document"""
        return await self.structure_parser.parse(result)

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "agent_type": self.agent_type,
            "model": self.model,
            "skills": self.skills,
            "supported_formats": ["epub", "pdf"],
            "features": [
                "metadata_extraction",
                "toc_extraction",
                "chapter_extraction",
                "text_cleaning",
                "structure_parsing",
            ],
        }


# Role Pool Integration
def create_extractor_role_config() -> Dict[str, Any]:
    """Create role configuration for MCP-S RolePool"""
    return {
        "role_id": "extractor",
        "role_name": "内容提取 Agent",
        "agent_id": "opencode",
        "model": "opencode/minimax-m2.5-free",
        "max_concurrent_tasks": 3,
        "warm_up": False,
        "timeout_seconds": 300,
        "metadata": {
            "skills": [
                "epub-parser",
                "pdf-parser",
                "text-extractor",
                "structure-parser",
            ],
            "supported_formats": ["epub", "pdf"],
            "description": "Extracts content from EPUB and PDF files",
        },
    }


# Example usage
async def main():
    """Example usage of Extractor Agent"""
    agent = ExtractorAgent()

    print("=" * 60)
    print("Extractor Agent - MCP-S")
    print("=" * 60)
    print(f"\nRole: {agent.role_name}")
    print(f"Skills: {', '.join(agent.skills)}")
    print(f"Model: {agent.model}")
    print()

    # Display capabilities
    caps = agent.get_capabilities()
    print("Capabilities:")
    for key, value in caps.items():
        print(f"  {key}: {value}")
    print()

    print("PyMuPDF Available:", PYMUPDF_AVAILABLE)
    print()

    # Example: Process a file (uncomment to use)
    # result = await agent.process("path/to/book.epub")
    # if result.success:
    #     print(f"Title: {result.metadata.get('title', 'N/A')}")
    #     print(f"Chapters: {len(result.chapters)}")
    # else:
    #     print(f"Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())
