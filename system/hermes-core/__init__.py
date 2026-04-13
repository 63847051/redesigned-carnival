"""
Hermes Core - 主入口

导出所有核心模块
"""

from core.snapshot_store import (
    SnapshotStore,
    AtomicWriter,
    get_snapshot_store,
    get_atomic_writer,
)
from core.fuzzy_patch import (
    FuzzyPatcher,
    PatchResult,
    fuzzy_match,
    calculate_similarity,
    find_closest_match,
)

from learning.auto_skill_creator import (
    AutoSkillCreator,
    TaskContext,
    create_skill_from_task,
)
from learning.auto_skill_improver import (
    AutoSkillImprover,
    UsageContext,
    ImprovementSuggestion,
    improve_skill,
)
from learning.self_guidance import (
    SelfGuidance,
    get_self_guidance,
    should_inject_guidance,
)

from search.fts5_search import (
    SessionSearch,
    get_session_search,
    search_sessions,
    index_session,
)
from search.llm_summarizer import (
    LLMSummarizer,
    SummaryResult,
    get_llm_summarizer,
    summarize_search_results,
)

from modeling.honcho_lite import (
    HonchoLite,
    UserProfile,
    UserConclusion,
    get_honcho,
    get_user_profile,
    search_user_history,
    reason_about_user,
    save_user_conclusion,
)

__version__ = "0.1.0"

__all__ = [
    "SnapshotStore",
    "AtomicWriter",
    "get_snapshot_store",
    "get_atomic_writer",
    "FuzzyPatcher",
    "PatchResult",
    "fuzzy_match",
    "calculate_similarity",
    "find_closest_match",
    "AutoSkillCreator",
    "TaskContext",
    "create_skill_from_task",
    "AutoSkillImprover",
    "UsageContext",
    "ImprovementSuggestion",
    "improve_skill",
    "SelfGuidance",
    "get_self_guidance",
    "should_inject_guidance",
    "SessionSearch",
    "get_session_search",
    "search_sessions",
    "index_session",
    "LLMSummarizer",
    "SummaryResult",
    "get_llm_summarizer",
    "summarize_search_results",
    "HonchoLite",
    "UserProfile",
    "UserConclusion",
    "get_honcho",
    "get_user_profile",
    "search_user_history",
    "reason_about_user",
    "save_user_conclusion",
]
