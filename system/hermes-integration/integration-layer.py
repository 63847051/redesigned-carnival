"""
Hermes Agent Integration Layer - OpenClaw 集成层

将 Hermes 核心功能集成到 OpenClaw 系统
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# 添加 Hermes 核心到路径
hermes_core_path = Path(__file__).parent.parent / "hermes-core"
sys.path.insert(0, str(hermes_core_path))

try:
    # 导入 Hermes 核心模块
    from learning.auto_skill_creator import AutoSkillCreator
    from learning.auto_skill_improver import AutoSkillImprover
    from modeling.honcho_lite import HonchoLite
    from search.fts5_search import SessionSearch
    from search.llm_summarizer import LLMSummarizer
    from fuzzy_patch import FuzzyPatchSystem
    from knowledge_persistence import KnowledgePersistenceSystem
    from snapshot_atomic import SnapshotAtomicSystem
    
    HERMES_AVAILABLE = True
except ImportError as e:
    HERMES_AVAILABLE = False
    print(f"⚠️ Hermes 核心模块不可用: {e}")


class HermesIntegration:
    """Hermes 集成层（主接口）"""
    
    def __init__(self, config_path: str = None):
        """初始化集成层"""
        self.config = self._load_config(config_path)
        self.enabled = self.config.get("integration", {}).get("enabled", False)
        
        if not self.enabled:
            print("ℹ️ Hermes 集成未启用")
            return
        
        if not HERMES_AVAILABLE:
            print("❌ Hermes 核心模块不可用，集成失败")
            self.enabled = False
            return
        
        # 初始化核心模块
        self._init_modules()
        self._setup_logging()
        
    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置"""
        if config_path is None:
            config_path = Path(__file__).parent / "hermes-config.json"
        
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        
        return {"integration": {"enabled": False}}
    
    def _init_modules(self):
        """初始化核心模块"""
        config = self.config
        
        # 学习子系统
        if config.get("core_modules", {}).get("learning", {}).get("enabled"):
            learning_config = config["core_modules"]["learning"]
            
            if learning_config.get("auto_skill_creator", {}).get("enabled"):
                self.skill_creator = AutoSkillCreator()
                print("✅ AutoSkillCreator 已初始化")
            
            if learning_config.get("auto_skill_improver", {}).get("enabled"):
                self.skill_improver = AutoSkillImprover()
                print("✅ AutoSkillImprover 已初始化")
        
        # 建模子系统
        if config.get("core_modules", {}).get("modeling", {}).get("enabled"):
            modeling_config = config["core_modules"]["modeling"]
            honcho_config = modeling_config.get("honcho_lite", {})
            
            self.user_model = HonchoLite(
                db_path=honcho_config.get("db_path", "/root/.openclaw/workspace/data/honcho.db")
            )
            print("✅ HonchoLite 已初始化")
        
        # 搜索子系统
        if config.get("core_modules", {}).get("search", {}).get("enabled"):
            search_config = config["core_modules"]["search"]
            
            if search_config.get("fts5_search", {}).get("enabled"):
                self.search = SessionSearch(
                    db_path=search_config["fts5_search"].get("db_path")
                )
                print("✅ SessionSearch 已初始化")
            
            if search_config.get("llm_summarizer", {}).get("enabled"):
                self.summarizer = LLMSummarizer()
                print("✅ LLMSummarizer 已初始化")
        
        # Fuzzy Patch
        if config.get("core_modules", {}).get("fuzzy_patch", {}).get("enabled"):
            fuzzy_config = config["core_modules"]["fuzzy_patch"]
            self.fuzzy_patch = FuzzyPatchSystem(
                min_confidence=fuzzy_config.get("min_confidence", 0.7)
            )
            print("✅ FuzzyPatchSystem 已初始化")
        
        # 知识持久化
        if config.get("core_modules", {}).get("knowledge_persistence", {}).get("enabled"):
            kp_config = config["core_modules"]["knowledge_persistence"]
            self.knowledge = KnowledgePersistenceSystem(
                db_path=kp_config.get("db_path")
            )
            print("✅ KnowledgePersistenceSystem 已初始化")
        
        # 快照系统
        if config.get("core_modules", {}).get("snapshot_atomic", {}).get("enabled"):
            sa_config = config["core_modules"]["snapshot_atomic"]
            self.snapshot = SnapshotAtomicSystem(
                snapshot_dir=sa_config.get("snapshot_dir")
            )
            print("✅ SnapshotAtomicSystem 已初始化")
    
    def _setup_logging(self):
        """设置日志"""
        log_config = self.config.get("monitoring", {})
        if not log_config.get("enabled", False):
            return
        
        log_path = log_config.get("log_path", "/root/.openclaw/workspace/logs/hermes.log")
        log_level = log_config.get("log_level", "info")
        
        # 创建日志目录
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 配置日志
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("HermesIntegration")
        self.logger.info("Hermes 集成层初始化完成")
    
    # ========== 触发器方法 ==========
    
    def on_task_completion(self, task_result: Dict[str, Any]):
        """任务完成触发器"""
        if not self.enabled:
            return
        
        self.logger.info(f"任务完成: {task_result.get('task_id')}")
        
        # 提取学习内容
        if hasattr(self, 'skill_creator'):
            # 记录任务完成用于后续技能创建
            self.logger.info(f"任务完成，可用于技能创建: {task_result.get('task_id')}")
        
        # 更新知识库
        if hasattr(self, 'knowledge'):
            self.knowledge.learn(
                key=f"task_{task_result.get('task_id')}",
                value=task_result,
                category="project"
            )
        
        # 改进技能
        if hasattr(self, 'skill_improver'):
            # 记录任务完成用于后续技能改进
            self.logger.info("任务完成，可用于技能改进")
    
    def on_session_start(self, session_id: str):
        """会话开始触发器"""
        if not self.enabled:
            return
        
        self.logger.info(f"会话开始: {session_id}")
        
        # 加载用户模型
        if hasattr(self, 'user_model'):
            # 使用默认用户 ID
            user_id = "default_user"
            user_profile = self.user_model.profile(user_id)
            self.logger.info(f"用户模型加载完成: {user_id}")
        
        # 加载最近上下文
        if hasattr(self, 'search'):
            recent_sessions = self.search.get_recent_sessions(limit=5)
            self.logger.info(f"加载最近上下文: {len(recent_sessions)} 个会话")
    
    def on_session_end(self, session_id: str, session_data: Dict):
        """会话结束触发器"""
        if not self.enabled:
            return
        
        self.logger.info(f"会话结束: {session_id}")
        
        # 保存用户模型
        if hasattr(self, 'user_model'):
            # 记录会话交互
            user_id = "default_user"
            self.user_model.record_interaction(
                user_id=user_id,
                content=f"Session {session_id} ended",
                metadata=session_data
            )
            self.logger.info("用户模型已更新")
        
        # 创建快照
        if hasattr(self, 'snapshot'):
            # 快照关键文件
            critical_files = [
                "/root/.openclaw/workspace/MEMORY.md",
                "/root/.openclaw/workspace/IDENTITY.md"
            ]
            
            for file_path in critical_files:
                if Path(file_path).exists():
                    # 读取文件内容
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # 创建快照
                    self.snapshot.save_state(
                        file_path,
                        content=content,
                        description=f"Session end: {session_id}"
                    )
            
            self.logger.info("会话快照已创建")
    
    def on_error(self, error: Exception, context: Dict):
        """错误触发器"""
        if not self.enabled:
            return
        
        self.logger.error(f"错误发生: {str(error)}", exc_info=True)
        
        # 记录错误到知识库
        if hasattr(self, 'knowledge'):
            self.knowledge.learn(
                key=f"error_{type(error).__name__}",
                value={
                    "error": str(error),
                    "context": context,
                    "timestamp": str(Path.ctime(Path(error.__traceback__.tb_frame.f_code.co_filename)))
                },
                category="system"
            )
        
        # 创建紧急快照
        if hasattr(self, 'snapshot'):
            critical_files = [
                "/root/.openclaw/workspace/MEMORY.md",
                "/root/.openclaw/openclaw.json"
            ]
            
            for file_path in critical_files:
                if Path(file_path).exists():
                    self.snapshot.save_state(
                        file_path,
                        description=f"Error snapshot: {type(error).__name__}",
                        create_snapshot=True
                    )
            
            self.logger.info("错误快照已创建")
    
    # ========== 工具方法 ==========
    
    def search_knowledge(self, query: str, category: str = None) -> list:
        """搜索知识"""
        if not self.enabled or not hasattr(self, 'knowledge'):
            return []
        
        return self.knowledge.search_knowledge(query, category)
    
    def get_user_profile(self) -> Dict:
        """获取用户画像"""
        if not self.enabled or not hasattr(self, 'user_model'):
            return {}
        
        return self.user_model.get_profile()
    
    def create_snapshot(self, file_path: str, description: str = "") -> bool:
        """创建快照"""
        if not self.enabled or not hasattr(self, 'snapshot'):
            return False
        
        return self.snapshot.save_state(
            file_path,
            description=description,
            create_snapshot=True
        )
    
    def apply_fuzzy_patch(self, file_path: str, old_code: str, new_code: str) -> bool:
        """应用模糊补丁"""
        if not self.enabled or not hasattr(self, 'fuzzy_patch'):
            return False
        
        result = self.fuzzy_patch.patch_file(file_path, old_code, new_code)
        return result.success


# 全局单例
_hermes_instance: Optional[HermesIntegration] = None


def get_hermes() -> HermesIntegration:
    """获取 Hermes 集成实例（单例）"""
    global _hermes_instance
    
    if _hermes_instance is None:
        _hermes_instance = HermesIntegration()
    
    return _hermes_instance


if __name__ == "__main__":
    # 测试
    hermes = get_hermes()
    
    if hermes.enabled:
        print("✅ Hermes 集成层测试成功")
        
        # 测试触发器
        hermes.on_session_start("test_session")
        hermes.on_task_completion({"task_id": "test_123", "status": "completed"})
        hermes.on_session_end("test_session", {"duration": 60})
    else:
        print("❌ Hermes 集成层未启用")
