#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
RAW_DIR = WORKSPACE / "knowledge-base/raw"
WIKI_DIR = WORKSPACE / "knowledge-base/wiki"

print("🧠 测试: Karpathy 编译器")
print("=" * 60)
print("")

# Step 1: 扫描文件
print("📂 Step 1: 扫描 raw/...")
md_files = list(RAW_DIR.glob("**/*.md"))
print(f"   找到 {len(md_files)} 个文件")

# Step 2: 简单编译
print("   Step 2: 简单编译...")
compiled = []
for f in md_files[:10]:  # 只处理前 10 个
    try:
        content = f.read_text(encoding='utf-8', errors='ignore')[:500]
        compiled.append({
            'path': str(f.relative_to(WORKSPACE)),
            'summary': content[:100] + "...",
            'keywords': ['test'],
            'concepts': ['test']
        })
    except:
        pass

print(f"   编译了 {len(compiled)} 个文件")

# Step 3: 生成 Wiki
print("   Step 3: 生成 Wiki...")
for item in compiled:
    path = WIKI_DIR / item['path'].split('/')[-1]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"# {item['path']}\n\n")
        f.write(f"**摘要**: {item['summary']}\n\n")

print("   ✅ Wiki 已生成")

# Step 4: 生成索引
print("   Step 4: 生成索引...")
index = {
    'total': len(compiled),
    'files': [c['path'] for c in compiled],
    'updated': str(datetime.now())
}

with open(WIKI_DIR / "index.md", 'w', encoding='utf-8') as f:
    f.write("# 知识库索引\n\n")
    f.write(f"**更新时间**: {index['updated']}\n\n")
    f.write(f"**文档总数**: {index['total']}\n\n")

print("   ✅ 索引已生成")

print("")
print("✅ 测试完成！")
print(f"📂 Wiki 位置: {WIKI_DIR}")
print(f"📄 索引文件: {WIKI_DIR}/index.md")
