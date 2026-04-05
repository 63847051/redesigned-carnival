#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识编译器 - Karpathy 原版
使用 Karpathy 的核心 Prompt
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
RAW_DIR = WORKSPACE / "knowledge-base/raw"
WIKI_DIR = WORKSPACE / "knowledge-base/wiki"
INDEX_FILE = WIKI_DIR / "index.md"


class KarpathyKnowledgeCompiler:
    """Karpathy 知识编译器"""
    
    def __init__(self):
        self.raw_dir = RAW_DIR
        self.wiki_dir = WIKI_DIR
        self.wiki_dir.mkdir(exist_ok=True, parents=True)
    
    def compile(self) -> Dict:
        """编译知识库"""
        print("🧠 Karpathy 知识编译器")
        print("=" * 60)
        print("")
        
        # Step 1: 扫描 raw/ 目录
        print("📂 Step 1: 扫描原始数据...")
        md_files = list(self.raw_dir.glob("**/*.md"))
        print(f"   找到 {len(md_files)} 个文件")
        
        # Step 2: LLM 编译
        print("   Step 2: LLM 编译...")
        compiled = self._llm_compile(md_files)
        
        # Step 3: 生成 Wiki
        print("   Step 3: 生成 Wiki...")
        self._generate_wiki(compiled)
        
        # Step 4: 生成索引
        print("   Step 4: 生成索引...")
        index = self._build_index(compiled)
        
        # Step 5: 保存
        print("   Step 5: 保存...")
        self._save_index(index)
        
        return {
            'total_files': len(md_files),
            'compiled': len(compiled),
            'concepts': len(index.get('concepts', {}))
        }
    
    def _llm_compile(self, files: List[Path]) -> List[Dict]:
        """使用 LLM 编译"""
        compiled = []
        
        for i, file in enumerate(files[:10], 1):  # 限制前 10 个
            print(f"   [{i}/{min(10, len(files))}] 编译: {file.relative_to(self.raw_dir)}")
            
            # 读取文件
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                
                # Karpathy 的核心 Prompt
                prompt = f"""你是一个知识编译器。

请分析以下文档，提取关键信息：

文档路径: {file}
文档内容（前 2000 字）:
{content[:2000]}

任务:
1. 生成简短摘要（50 字内）
2. 提取 3-5 个关键词
3. 识别相关概念
4. 建议链接到其他文档

返回格式（JSON）:
{{
  "path": "{file}",
  "summary": "摘要",
  "keywords": ["关键词1", "关键词2"],
  "concepts": ["概念1", "概念2"],
  "related": []
}}"""
                
                # 调用 LLM
                try:
                    result = subprocess.run(
                        ['sessions_spawn', '-runtime', 'subagent', '-model', 'glmcode/glm-4.5-air'],
                        input=prompt,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    # 解析结果
                    try:
                        data = json.loads(result.stdout.strip())
                        compiled.append(data)
                    except:
                        # 降级方案：简单摘要
                        compiled.append({
                            'path': str(file.relative_to(WORKSPACE)),
                            'summary': content[:100] + "...",
                            'keywords': ['test'],
                            'concepts': ['test'],
                            'related': []
                        })
                except Exception as e:
                    print(f"      ⚠️ LLM 调用失败: {e}")
                    compiled.append({
                        'path': str(file.relative_to(WORKSPACE)),
                        'summary': content[:100] + "...",
                        'keywords': [],
                        'concepts': [],
                        'related': []
                    })
                
            except Exception as e:
                print(f"      ⚠️ 文件读取失败: {e}")
        
        return compiled
    
    def _generate_wiki(self, compiled: List[Dict]):
        """生成 Wiki 文件"""
        for item in compiled:
            # 生成文件名
            filename = item['path'].split('/')[-1]
            path = self.wiki_dir / "articles" / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入 Wiki 文件
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"# {filename}\n\n")
                f.write(f"**摘要**: {item['summary']}\n\n")
                f.write(f"**关键词**: {', '.join(item.get('keywords', []))}\n\n")
                f.write(f"**概念**: {', '.join(item.get('concepts', []))}\n\n")
    
    def _build_index(self, compiled: List[Dict]) -> Dict:
        """构建索引"""
        index = {
            'total': len(compiled),
            'files': [c['path'] for c in compiled],
            'keywords': {},
            'concepts': {},
            'updated': str(datetime.now())
        }
        
        # 关键词索引
        for c in compiled:
            for kw in c.get('keywords', []):
                if kw not in index['keywords']:
                    index['keywords'][kw] = []
                index['keywords'][kw].append(c['path'])
        
        # 概念索引
        for c in compiled:
            for concept in c.get('concepts', []):
                if concept not in index['concepts']:
                    index['concepts'][concept] = []
                index['concepts'][concept].append(c['path'])
        
        return index
    
    def _save_index(self, index: Dict):
        """保存索引"""
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write("# 知识库索引\n\n")
            f.write(f"**更新时间**: {index['updated']}\n\n")
            f.write(f"**文档总数**: {index['total']}\n\n")
            
            f.write("## 关键词索引\n\n")
            for kw, paths in index['keywords'].items():
                f.write(f"### {kw}\n")
                for path in paths:
                    f.write(f"- {path}\n")
                f.write("\n")
            
            f.write("## 概念索引\n\n")
            for concept, paths in index['concepts'].items():
                f.write(f"### {concept}\n")
                for path in paths:
                    f.write(f"- {path}\n")
                f.write("\n")


def main():
    """主函数"""
    compiler = KarpathyKnowledgeCompiler()
    
    # 编译
    stats = compiler.compile()
    
    print("")
    print("✅ 编译完成！")
    print(f"   总文件数: {stats['total_files']}")
    print(f"   编译文件数: {stats['compiled']}")
    print(f"   概念数: {stats['concepts']}")
    print("")
    print(f"📂 Wiki 位置: {WIKI_DIR}")
    print(f"📄 索引文件: {INDEX_FILE}")


if __name__ == "__main__":
    main()
