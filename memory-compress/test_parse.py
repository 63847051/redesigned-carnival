"""测试 MEMORY.md 解析"""

import re

test_content = """
# MEMORY.md

## 📝 今日决策（2026-04-01）

- 决策 1
- 决策 2

## 🧠 核心学习（2026-04-01）

- 学习 1
- 学习 2

## 📝 今日决策（2026-04-02）

- 决策 3
- 决策 4
"""

# 测试正则表达式
pattern = r'## 📝 今日决策\((\d{4}-\d{2}-\d{2})\)'
matches = list(re.finditer(pattern, test_content))

print(f"匹配到 {len(matches)} 个日期")
for match in matches:
    print(f"  - {match.group(1)}")

# 测试分割
sections = re.split(pattern, test_content)
print(f"\n分割后 {len(sections)} 个部分")
for i, section in enumerate(sections[:5]):
    preview = section.strip()[:100]
    print(f"  [{i}]: {preview}...")
