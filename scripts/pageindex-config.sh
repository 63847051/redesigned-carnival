# pageindex-rag 配置文件
# 用于优化检索参数和提示词

# 检索参数
RECALL_COUNT=10          # 初始召回数量（QMD）
FINAL_COUNT=5           # 最终返回数量
CACHE_TTL=300           # 缓存过期时间（秒）

# QMD 配置
QMD_SEARCH_CMD="qmd search memory"
QMD_MIN_SCORE=70        # 最低相关性分数（0-100）

# 文件名匹配权重
FILENAME_MATCH_WEIGHT=0.8  # 文件名匹配权重（0-1）
QMD_MATCH_WEIGHT=1.0       # QMD 匹配权重（0-1）

# 输出格式
SHOW_PREVIEW_LINES=2     # 显示文件预览行数
SHOW_FULL_PATH=0         # 是否显示完整路径（0/1）

# 性能优化
ENABLE_CACHE=1           # 是否启用缓存（0/1）
ENABLE_PARALLEL=0        # 是否启用并行搜索（0/1）

# LLM 配置（用于未来的 LLM 排序）
LLM_MODEL="glmcode/glm-4.7"
LLM_TIMEOUT=30           # LLM 超时时间（秒）
LLM_MAX_TOKENS=500       # 最大 token 数

# 调试模式
DEBUG=0                  # 是否显示调试信息（0/1）
VERBOSE=0                # 是否显示详细信息（0/1）
