# 飞书集成 - 实用解决方案

基于你提供的飞书文档，这里提供一个实用的解决方案

---

## 🎯 快速解决方案

### 方案 1: 使用飞书文档 API（推荐）

如果你的飞书文档是关于 API 使用的，可以尝试使用**飞书文档 API**而不是**多维表格 API**。

**优势**:
- ✅ 更简单的 API
- ✅ 不需要创建表格
- ✅ 直接写入文档

**实现**:
```python
import requests
import json

def append_to_feishu_doc(content: str):
    """追加内容到飞书文档"""
    # 飞书文档 API
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}/children"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "children": [
            {
                "block_type": 1,  # 文本块
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": content
                            }
                        }
                    ]
                }
            }
        ],
        "index": -1  # 追加到末尾
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

---

### 方案 2: 创建简化的飞书表格

如果文档中提到了表格创建，可以尝试创建一个**最小化配置**的表格：

**最小字段配置**（只包含必需字段）:

```python
# 只需要 2 个字段即可开始使用
minimal_fields = {
    "content": "文本",        # 记忆内容
    "created_at": "日期"     # 创建时间
}
```

**优点**:
- ✅ 更简单的配置
- ✅ 减少出错可能
- ✅ 快速开始

---

### 方案 3: 使用飞书 Webhook（最简单）

如果你的飞书文档中提到了 Webhook，这是最简单的方案：

```python
import requests
import json

def send_to_feishu_webhook(content: str, webhook_url: str):
    """通过 Webhook 发送到飞书"""
    data = {
        "msg_type": "text",
        "content": {
            "text": content
        }
    }
    
    response = requests.post(webhook_url, json=data)
    return response.json()

# 使用示例
webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
send_to_feishu_webhook("记忆：用户喜欢使用 Python 编程", webhook_url)
```

**优势**:
- ✅ 最简单
- ✅ 不需要配置表格
- ✅ 立即可用

---

## 🔍 从飞书文档中获取关键信息

请检查你提供的飞书文档，查找以下信息：

### 1. API 端点

文档中可能提到了：
- `/open-apis/bitable/v1/apps` - 多维表格 API
- `/open-apis/docx/v1/documents` - 文档 API
- `/open-apis/bot/v2/hook` - Webhook API

### 2. 认证方式

查找：
- `tenant_key` - 租户密钥
- `app_id` - 应用 ID
- `app_secret` - 应用密钥
- `access_token` - 访问令牌

### 3. 权限配置

查找需要的权限：
- `bitable:app` - 多维表格权限
- `bitable:app:readonly` - 只读权限
- `docx:document` - 文档权限

---

## 🎯 推荐方案（基于你的情况）

### 如果文档中提到了 Webhook

**使用 Webhook**（最简单）：

```python
import requests

def send_memory_to_feishu(content: str, importance: str):
    """发送记忆到飞书"""
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
    
    message = f"""
📝 记忆记录

内容: {content}
重要性: {importance}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    data = {
        "msg_type": "text",
        "content": {"text": message}
    }
    
    requests.post(webhook_url, json=data)

# 使用
send_memory_to_feishu("用户喜欢使用 Python 编程", "HIGH")
```

### 如果文档中提到了文档 API

**使用飞书文档**（推荐）：

```python
import requests

def append_memory_to_doc(doc_id: str, content: str):
    """追加记忆到飞书文档"""
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/doc:{doc_id}/children"
    
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }
    
    data = {
        "children": [{
            "block_type": 1,
            "text": {
                "elements": [{
                    "text_run": {
                        "content": f"📝 {content}\n"
                    }
                }]
            }
        }],
        "index": -1
    }
    
    requests.post(url, headers=headers, json=data)

# 使用
append_memory_to_doc("MFK7dDFLFoVlOGxWCv5cTXKmnMh", "用户喜欢使用 Python 编程")
```

---

## 💡 临时解决方案

如果飞书集成暂时有问题，可以使用：

### 1. 本地文件备份

```python
import json
from datetime import datetime

def backup_to_file(content: str, importance: str):
    """备份到本地文件"""
    memory = {
        "content": content,
        "importance": importance,
        "created_at": datetime.now().isoformat()
    }
    
    with open("memories.jsonl", "a") as f:
        f.write(json.dumps(memory, ensure_ascii=False) + "\n")

# 使用
backup_to_file("用户喜欢使用 Python 编程", "HIGH")
```

### 2. 数据库存储

```python
import sqlite3

def init_db():
    """初始化 SQLite 数据库"""
    conn = sqlite3.connect("memories.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            importance TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    return conn

def save_memory(conn, content: str, importance: str):
    """保存记忆到数据库"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memories (content, importance) VALUES (?, ?)",
        (content, importance)
    )
    conn.commit()

# 使用
conn = init_db()
save_memory(conn, "用户喜欢使用 Python 编程", "HIGH")
```

---

## 🎯 最终建议

**基于你的情况**：

1. **如果飞书文档提供了 Webhook** → 使用 Webhook（最简单）
2. **如果飞书文档提供了文档 API** → 使用文档 API（推荐）
3. **如果暂时无法集成** → 使用本地文件或数据库（临时）

---

## 📞 下一步

**请告诉我**：
1. 飞书文档中提到了什么 API？（Webhook/文档/表格）
2. 是否提供了 `app_id`、`app_secret` 等凭证？
3. 是否需要获取 `access_token`？

**根据你的回答，我可以为你创建具体的集成代码！** 😊

---

**临时方案**: 继续使用本地记忆存储（`enable_feishu=False`），等飞书集成准备好后再启用。
