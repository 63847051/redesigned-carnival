"""测试决策提取"""

from rule_extractor import extract_decisions, _extract_text_from_message

messages = [
    {
        "role": "user",
        "content": "我们决定采用基于规则的压缩方案",
        "timestamp": "2026-04-09T10:10:00"
    }
]

# 测试文本提取
content = _extract_text_from_message(messages[0])
print(f"提取的文本: '{content}'")
print(f"文本长度: {len(content)}")

# 测试关键词匹配
keywords = ["决定", "选择", "采用", "方案"]
content_lower = content.lower()
print(f"小写文本: '{content_lower}'")

for keyword in keywords:
    keyword_lower = keyword.lower()
    if keyword_lower in content_lower:
        print(f"✅ 匹配到关键词: {keyword}")
    else:
        print(f"❌ 未匹配到关键词: {keyword}")

# 测试提取
decisions = extract_decisions(messages)
print(f"提取的决策: {decisions}")
