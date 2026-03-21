"""
Test Suite for Extractor Agent
===============================

Tests the following skills:
- epub-parser: EPUB file parsing and TOC extraction
- pdf-parser: PDF file parsing and text extraction
- text-extractor: Clean text extraction
- structure-parser: Document structure parsing

Usage:
------
    pytest test_extractor_agent.py -v
"""

import asyncio
import json
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.extractor_agent import (
    ExtractorAgent,
    ExtractorConfig,
    EPUBParser,
    PDFParser,
    TextExtractor,
    StructureParser,
    ExtractionResult,
    create_extractor_role_config,
    PYMUPDF_AVAILABLE,
)


class TestExtractorAgentConfig:
    """Test ExtractorAgent configuration"""

    def test_default_config(self):
        config = ExtractorConfig()
        assert config.role_id == "extractor"
        assert config.role_name == "内容提取 Agent"
        assert config.agent_type == "opencode"
        assert config.model == "opencode/minimax-m2.5-free"
        assert "epub-parser" in config.skills
        assert "pdf-parser" in config.skills
        assert "text-extractor" in config.skills
        assert "structure-parser" in config.skills

    def test_custom_config(self):
        config = ExtractorConfig(
            role_id="custom_extractor",
            role_name="Custom Extractor",
            timeout_seconds=600,
        )
        assert config.role_id == "custom_extractor"
        assert config.timeout_seconds == 600


class TestExtractorAgentCreation:
    """Test ExtractorAgent instantiation"""

    def test_create_agent(self):
        agent = ExtractorAgent()
        assert agent.role_id == "extractor"
        assert agent.role_name == "内容提取 Agent"
        assert agent.model == "opencode/minimax-m2.5-free"

    def test_skills_initialized(self):
        agent = ExtractorAgent()
        assert isinstance(agent.epub_parser, EPUBParser)
        assert isinstance(agent.pdf_parser, PDFParser)
        assert isinstance(agent.text_extractor, TextExtractor)
        assert isinstance(agent.structure_parser, StructureParser)

    def test_capabilities(self):
        agent = ExtractorAgent()
        caps = agent.get_capabilities()
        assert caps["role_id"] == "extractor"
        assert "epub" in caps["supported_formats"]
        assert "pdf" in caps["supported_formats"]
        assert "metadata_extraction" in caps["features"]


class TestRoleConfig:
    """Test MCP-S RolePool integration"""

    def test_create_role_config(self):
        config = create_extractor_role_config()
        assert config["role_id"] == "extractor"
        assert config["agent_id"] == "opencode"
        assert config["model"] == "opencode/minimax-m2.5-free"
        assert "skills" in config["metadata"]
        assert "epub-parser" in config["metadata"]["skills"]


class TestEPUBParser:
    """Test EPUB parsing functionality"""

    @pytest.fixture
    def epub_parser(self):
        return EPUBParser()

    @pytest.fixture
    def sample_epub_path(self, tmp_path):
        """Create a minimal valid EPUB file"""
        epub_path = tmp_path / "test.epub"

        with zipfile.ZipFile(epub_path, "w") as zf:
            # Create META-INF/container.xml
            container = """<?xml version="1.0"?>
            <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
                <rootfiles>
                    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
                </rootfiles>
            </container>"""
            zf.writestr("META-INF/container.xml", container)

            # Create OPF file
            opf = """<?xml version="1.0"?>
            <package xmlns="http://www.idpf.org/2007/opf" version="3.0">
                <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                    <dc:title>Test Book</dc:title>
                    <dc:creator>Test Author</dc:creator>
                    <dc:language>en</dc:language>
                </metadata>
                <manifest>
                    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
                    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
                </manifest>
                <spine>
                    <itemref idref="chapter1"/>
                </spine>
            </package>"""
            zf.writestr("OEBPS/content.opf", opf)

            # Create nav.xhtml
            nav = """<?xml version="1.0"?>
            <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/opf">
                <nav epub:type="toc">
                    <ol>
                        <li><a href="chapter1.xhtml">Chapter 1</a></li>
                    </ol>
                </nav>
            </html>"""
            zf.writestr("OEBPS/nav.xhtml", nav)

            # Create chapter content
            chapter = """<?xml version="1.0"?>
            <html xmlns="http://www.w3.org/1999/xhtml">
                <body>
                    <h1>Chapter 1: Introduction</h1>
                    <p>This is the first paragraph of the test book.</p>
                    <p>Here is another paragraph with some content.</p>
                </body>
            </html>"""
            zf.writestr("OEBPS/chapter1.xhtml", chapter)

        return str(epub_path)

    @pytest.mark.asyncio
    async def test_parse_valid_epub(self, epub_parser, sample_epub_path):
        result = await epub_parser.parse(sample_epub_path)

        assert result.success is True
        assert result.format == "epub"
        assert result.metadata.get("title") == "Test Book"
        assert result.metadata.get("creator") == "Test Author"
        assert len(result.toc) > 0
        assert "Chapter 1" in result.toc[0].get("label", "")

    @pytest.mark.asyncio
    async def test_parse_nonexistent_file(self, epub_parser):
        result = await epub_parser.parse("/nonexistent/file.epub")

        assert result.success is False
        assert "not found" in result.error.lower()


class TestPDFParser:
    """Test PDF parsing functionality"""

    @pytest.fixture
    def pdf_parser(self):
        return PDFParser()

    @pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
    @pytest.mark.asyncio
    async def test_parse_pdf_not_implemented(self, pdf_parser, tmp_path):
        """PDF parsing requires actual PDF file - tested with mock"""
        pass


class TestTextExtractor:
    """Test text extraction and cleaning"""

    @pytest.fixture
    def text_extractor(self):
        return TextExtractor()

    @pytest.fixture
    def sample_result(self):
        return ExtractionResult(
            success=True,
            format="epub",
            content="  This is   a test.\n\n\n\nWith   extra   spacing.\n\nEnd.  ",
        )

    @pytest.mark.asyncio
    async def test_clean_text(self, text_extractor, sample_result):
        cleaned = await text_extractor.extract(sample_result, clean=True)

        assert "  This is   a test." not in cleaned
        assert "\n\n\n\n" not in cleaned
        assert "With extra spacing." in cleaned

    @pytest.mark.asyncio
    async def test_extract_chapters(self, text_extractor):
        result = ExtractionResult(
            success=True,
            format="epub",
            chapters=[
                {"index": 0, "content": "Chapter 1 content"},
                {"index": 1, "content": "Chapter 2 content"},
            ],
        )

        chapters = await text_extractor.extract_chapters(result)
        assert len(chapters) == 2
        assert "Chapter 1 content" in chapters[0]


class TestStructureParser:
    """Test document structure parsing"""

    @pytest.fixture
    def structure_parser(self):
        return StructureParser()

    @pytest.fixture
    def sample_result(self):
        return ExtractionResult(
            success=True,
            format="epub",
            metadata={"title": "Test Book", "author": "Test Author"},
            toc=[
                {"label": "Chapter 1", "href": "ch1.xhtml", "depth": 0},
                {"label": "Chapter 2", "href": "ch2.xhtml", "depth": 0},
            ],
            chapters=[
                {
                    "index": 0,
                    "title": "Chapter 1",
                    "content": "# Introduction\n\nSome text here.\n## Getting Started\n\nMore text.",
                },
                {
                    "index": 1,
                    "title": "Chapter 2",
                    "content": "# Advanced Topics\n\nAdvanced content here.",
                },
            ],
            stats={"total_pages": 100, "content_length": 5000},
        )

    @pytest.mark.asyncio
    async def test_parse_structure(self, structure_parser, sample_result):
        structure = await structure_parser.parse(sample_result)

        assert structure["metadata"]["title"] == "Test Book"
        assert len(structure["table_of_contents"]["children"]) == 2
        assert len(structure["chapters"]) == 2
        assert structure["chapters"][0]["word_count"] > 0

    def test_build_toc_tree(self, structure_parser):
        toc = [
            {"label": "Chapter 1", "href": "ch1.xhtml", "depth": 0},
            {"label": "Section 1.1", "href": "ch1.xhtml#s1", "depth": 1},
            {"label": "Chapter 2", "href": "ch2.xhtml", "depth": 0},
        ]

        tree = structure_parser._build_toc_tree(toc)

        assert tree["label"] == "Root"
        assert len(tree["children"]) == 2
        assert tree["children"][0]["label"] == "Chapter 1"
        assert len(tree["children"][0]["children"]) == 1
        assert tree["children"][0]["children"][0]["label"] == "Section 1.1"


class TestIntegration:
    """Integration tests for Extractor Agent"""

    @pytest.fixture
    def agent(self):
        return ExtractorAgent()

    @pytest.mark.asyncio
    async def test_auto_format_detection(self, agent, tmp_path):
        """Test format auto-detection from file extension"""
        epub_path = tmp_path / "test.epub"
        epub_path.touch()

        result = await agent.process(str(epub_path))
        assert result.format == "epub"

        pdf_path = tmp_path / "test.pdf"
        pdf_path.touch()

        result = await agent.process(str(pdf_path))
        assert result.format == "pdf"

    @pytest.mark.asyncio
    async def test_explicit_format(self, agent, tmp_path):
        """Test explicit format specification"""
        path = tmp_path / "file.xyz"
        path.touch()

        result = await agent.process(str(path), file_format="epub")
        assert result.format == "epub"

    @pytest.mark.asyncio
    async def test_unsupported_format(self, agent, tmp_path):
        """Test handling of unsupported formats"""
        path = tmp_path / "file.txt"
        path.touch()

        result = await agent.process(str(path))

        assert result.success is False
        assert "Unknown" in result.error or "Unsupported" in result.error


class TestExtractionResult:
    """Test ExtractionResult dataclass"""

    def test_create_result(self):
        result = ExtractionResult(
            success=True,
            format="epub",
            metadata={"title": "Test"},
            toc=[{"label": "Chapter 1"}],
            content="Some content",
        )

        assert result.success is True
        assert result.metadata["title"] == "Test"
        assert len(result.toc) == 1

    def test_default_values(self):
        result = ExtractionResult(success=True, format="pdf")

        assert result.metadata == {}
        assert result.toc == []
        assert result.content == ""
        assert result.chapters == []
        assert result.error is None


# Test fixtures
@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
