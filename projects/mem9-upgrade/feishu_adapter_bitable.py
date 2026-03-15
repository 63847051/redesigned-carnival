"""
飞书 Bitable 适配器 for mem9 记忆系统
使用现有的蓝色光标工作日志表格作为记忆存储后端
"""

import logging
import sys
from pathlib import Path

# 添加工作区路径
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from typing import List, Dict, Any, Optional
from datetime import datetime
from skills.feishu_worklog.bitable_manager import BitableManager

logger = logging.getLogger(__name__)


class FeishuMemoryBitable:
    """飞书多维表格记忆存储适配器
    
    将 mem9 记忆映射到现有的工作日志表格
    """
    
    # 字段映射
    FIELD_MAPPING = {
        "content": "内容",
        "importance": "优先级别",
        "memory_type": "项目状态",  # 临时复用
        "extraction_type": "项目类型",  # 临时复用
        "created_at": "创建日期",
        "source_turn_id": "附件",  # 临时复用（存储 ID）
    }
    
    # 重要性映射
    IMPORTANCE_MAPPING = {
        "CRITICAL": "第一优先",
        "HIGH": "重要",
        "MEDIUM": "普通",
        "LOW": "中",
        "MINIMAL": "普通",
    }
    
    # 记忆类型映射
    MEMORY_TYPE_MAPPING = {
        "SHORT_TERM": "待确认",
        "LONG_TERM": "待完成",
    }
    
    # 提取类型映射
    EXTRACTION_TYPE_MAPPING = {
        "PREFERENCE": "设计",
        "RULE": "施工",
        "TASK": "机电",
        "PROJECT": "现场",
        "IDENTITY": "设计",
        "MANUAL": "现场",
    }
    
    def __init__(self, app_token: str, table_id: str):
        """初始化适配器
        
        Args:
            app_token: 飞书多维表格 app token
            table_id: 表格 ID
        """
        self.manager = BitableManager(app_token, table_id)
        self.app_token = app_token
        self.table_id = table_id
        
    def set_access_token(self, access_token: str) -> None:
        """设置访问令牌"""
        self.manager.set_access_token(access_token)
        
    def add_memory(self, memory: Dict[str, Any]) -> bool:
        """添加记忆到飞书表格
        
        Args:
            memory: 记忆字典，包含以下字段：
                - content: 内容
                - importance: 重要性 (CRITICAL/HIGH/MEDIUM/LOW/MINIMAL)
                - memory_type: 记忆类型 (SHORT_TERM/LONG_TERM)
                - extraction_type: 提取类型
                - created_at: 创建时间
                - source_turn_id: 来源 ID
                - tags: 标签（可选）
        
        Returns:
            是否添加成功
        """
        try:
            # 映射字段
            record = {
                "内容": memory.get("content", ""),
                "优先级别": self.IMPORTANCE_MAPPING.get(
                    memory.get("importance", "MEDIUM"),
                    "普通"
                ),
                "项目状态": self.MEMORY_TYPE_MAPPING.get(
                    memory.get("memory_type", "SHORT_TERM"),
                    "待确认"
                ),
                "项目类型": self.EXTRACTION_TYPE_MAPPING.get(
                    memory.get("extraction_type", "PREFERENCE"),
                    "设计"
                ),
                "创建日期": self._format_date(memory.get("created_at")),
                "附件": memory.get("source_turn_id", ""),
                "备注": self._format_tags(memory.get("tags", [])),
            }
            
            # 添加到飞书
            result = self.manager.add_record(record)
            
            if result:
                logger.info(f"✅ 记忆已添加到飞书: {memory.get('content', '')[:50]}...")
            else:
                logger.warning(f"⚠️ 记忆添加失败: {memory.get('content', '')[:50]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 添加记忆失败: {e}")
            return False
    
    def query_memories(
        self, 
        filters: Optional[Dict] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """查询记忆
        
        Args:
            filters: 过滤条件
            limit: 返回数量限制
        
        Returns:
            记忆列表
        """
        try:
            records = self.manager.query_records(filters)
            
            # 转换为 mem9 格式
            memories = []
            for record in records[:limit]:
                memory = {
                    "content": record.get("内容", ""),
                    "importance": self._reverse_importance(
                        record.get("优先级别", "普通")
                    ),
                    "memory_type": self._reverse_memory_type(
                        record.get("项目状态", "待确认")
                    ),
                    "extraction_type": self._reverse_extraction_type(
                        record.get("项目类型", "设计")
                    ),
                    "created_at": record.get("创建日期", ""),
                    "source_turn_id": record.get("附件", ""),
                    "tags": self._parse_tags(record.get("备注", "")),
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"❌ 查询记忆失败: {e}")
            return []
    
    def _format_date(self, date_value: Any) -> str:
        """格式化日期"""
        if isinstance(date_value, datetime):
            return date_value.strftime("%Y/%m/%d")
        elif isinstance(date_value, str):
            return date_value
        else:
            return datetime.now().strftime("%Y/%m/%d")
    
    def _format_tags(self, tags: List[str]) -> str:
        """格式化标签"""
        if not tags:
            return ""
        return ", ".join(tags)
    
    def _parse_tags(self, notes: str) -> List[str]:
        """解析标签"""
        if not notes:
            return []
        return [tag.strip() for tag in notes.split(",") if tag.strip()]
    
    def _reverse_importance(self, value: str) -> str:
        """反向映射重要性"""
        mapping = {v: k for k, v in self.IMPORTANCE_MAPPING.items()}
        return mapping.get(value, "MEDIUM")
    
    def _reverse_memory_type(self, value: str) -> str:
        """反向映射记忆类型"""
        mapping = {v: k for k, v in self.MEMORY_TYPE_MAPPING.items()}
        return mapping.get(value, "SHORT_TERM")
    
    def _reverse_extraction_type(self, value: str) -> str:
        """反向映射提取类型"""
        mapping = {v: k for k, v in self.EXTRACTION_TYPE_MAPPING.items()}
        return mapping.get(value, "PREFERENCE")


# 测试代码
async def test_adapter():
    """测试适配器"""
    import asyncio
    
    # 配置
    app_token = "BISAbNgYXa7Do1sc36YcBChInnS"
    table_id = "tbl5s8TEZ0tKhEm7"
    
    # 创建适配器
    adapter = FeishuMemoryBitable(app_token, table_id)
    
    # 测试记忆
    test_memory = {
        "content": "测试记忆：用户喜欢使用 Python 编程",
        "importance": "HIGH",
        "memory_type": "LONG_TERM",
        "extraction_type": "PREFERENCE",
        "created_at": datetime.now(),
        "source_turn_id": "test_001",
        "tags": ["python", "编程"],
    }
    
    # 添加记忆
    print("📝 添加测试记忆...")
    success = adapter.add_memory(test_memory)
    
    if success:
        print("✅ 记忆添加成功！")
        
        # 查询记忆
        print("\n🔍 查询记忆...")
        memories = adapter.query_memories(limit=5)
        
        print(f"✅ 找到 {len(memories)} 条记忆:")
        for i, memory in enumerate(memories, 1):
            print(f"\n{i}. {memory['content']}")
            print(f"   重要性: {memory['importance']}")
            print(f"   类型: {memory['memory_type']}")
    else:
        print("❌ 记忆添加失败")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_adapter())
