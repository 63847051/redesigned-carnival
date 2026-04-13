"""
Fuzzy Patch System - 模糊匹配和自动补丁系统

基于 Hermes Agent 的 Fuzzy Patch 机制实现
"""

import re
import difflib
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CodeMatch:
    """代码匹配结果"""
    confidence: float
    matched_text: str
    start_line: int
    end_line: int


@dataclass
class PatchResult:
    """补丁应用结果"""
    success: bool
    patched_content: str
    changes_made: int
    warnings: List[str]
    
    def __str__(self):
        status = "✅ 成功" if self.success else "❌ 失败"
        return f"{status} | 变更: {self.changes_made} 处 | 警告: {len(self.warnings)}"


class FuzzyMatcher:
    """模糊匹配器"""
    
    def __init__(self, min_confidence: float = 0.7):
        self.min_confidence = min_confidence
        
    def normalize_code(self, code: str) -> str:
        """标准化代码"""
        code = re.sub(r'\s+', ' ', code)
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        return code.replace('"', "'").strip()
    
    def find_match(self, pattern: str, content: str, fuzzy: bool = True) -> Optional[CodeMatch]:
        """查找匹配"""
        if pattern in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if pattern in line:
                    return CodeMatch(confidence=1.0, matched_text=pattern, start_line=i+1, end_line=i+1)
        
        if fuzzy:
            pattern_norm = self.normalize_code(pattern)
            content_lines = content.split('\n')
            
            for i, line in enumerate(content_lines):
                line_norm = self.normalize_code(line)
                similarity = difflib.SequenceMatcher(None, pattern_norm, line_norm).ratio()
                
                if similarity >= self.min_confidence:
                    return CodeMatch(confidence=similarity, matched_text=line, start_line=i+1, end_line=i+1)
        
        return None


class PatchGenerator:
    """补丁生成器"""
    
    def apply_patch(self, content: str, old_code: str, new_code: str, fuzzy: bool = True) -> PatchResult:
        """应用补丁"""
        matcher = FuzzyMatcher()
        warnings = []
        
        match = matcher.find_match(old_code, content, fuzzy=fuzzy)
        
        if not match:
            return PatchResult(success=False, patched_content=content, changes_made=0, warnings=["未找到匹配"])
        
        if match.confidence < 0.8:
            warnings.append(f"匹配置信度较低: {match.confidence:.2f}")
        
        lines = content.split('\n')
        lines[match.start_line - 1] = new_code
        
        return PatchResult(success=True, patched_content='\n'.join(lines), changes_made=1, warnings=warnings)


class FuzzyPatchSystem:
    """模糊补丁系统（主接口）"""
    
    def __init__(self, min_confidence: float = 0.7):
        self.matcher = FuzzyMatcher(min_confidence)
        self.generator = PatchGenerator()
        self.history = []
        
    def patch_file(self, file_path: str, old_code: str, new_code: str, fuzzy: bool = True, backup: bool = True) -> PatchResult:
        """对文件应用补丁"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if backup:
                backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            result = self.generator.apply_patch(content, old_code, new_code, fuzzy)
            
            if result.success:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(result.patched_content)
                
                self.history.append({
                    'timestamp': datetime.now().isoformat(),
                    'file': file_path,
                    'changes': result.changes_made,
                    'success': True
                })
            
            return result
            
        except Exception as e:
            return PatchResult(success=False, patched_content="", changes_made=0, warnings=[f"错误: {str(e)}"])


if __name__ == "__main__":
    system = FuzzyPatchSystem()
    print("✅ Fuzzy Patch 系统初始化成功")
