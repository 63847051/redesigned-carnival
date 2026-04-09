-- OpenClaw Slock Server - 完整数据库 Schema
-- 版本: v1.0
-- 创建时间: 2026-04-07

-- =============================================================================
-- 消息表 (messages)
-- =============================================================================

CREATE TABLE IF NOT EXISTS messages (
    -- 主键
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 基本信息
    session_key TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    
    -- 元数据
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    message_id TEXT,
    channel_id TEXT,
    thread_id TEXT,
    
    -- 索引
    INDEX idx_session_key (session_key),
    INDEX idx_timestamp (timestamp),
    INDEX idx_channel (channel_id),
    INDEX idx_thread (thread_id)
);

-- =============================================================================
-- 任务表 (tasks)
-- =============================================================================

CREATE TABLE IF NOT EXISTS tasks (
    -- 主键
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 基本信息
    task_id TEXT UNIQUE NOT NULL,
    session_key TEXT NOT NULL,
    title TEXT,
    description TEXT,
    
    -- 状态管理
    status TEXT DEFAULT 'pending',  -- 'pending', 'claimed', 'in_progress', 'completed', 'failed'
    skills TEXT,  -- JSON array
    priority TEXT DEFAULT 'normal',  -- 'low', 'normal', 'high', 'urgent'
    
    -- 分配信息
    agent_id TEXT,
    claimed_at DATETIME,
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    
    -- 索引
    INDEX idx_session_key (session_key),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_agent (agent_id)
);

-- =============================================================================
-- 会话表 (sessions)
-- =============================================================================

CREATE TABLE IF NOT EXISTS sessions (
    -- 主键
    session_key TEXT PRIMARY KEY,
    
    -- 基本信息
    agent_id TEXT,
    agent_type TEXT,  -- 'subagent', 'acp', 'opencode'
    state TEXT DEFAULT 'cold_start',  -- 'cold_start', 'running', 'idle', 'sleep', 'stopped', 'error'
    driver_type TEXT,
    
    -- 进程信息
    process_id INTEGER,
    
    -- 统计信息
    message_count INTEGER DEFAULT 0,
    task_count INTEGER DEFAULT 0,
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME
);

-- =============================================================================
-- 频道表 (channels)
-- =============================================================================

CREATE TABLE IF NOT EXISTS channels (
    -- 主键
    channel_id TEXT PRIMARY KEY,
    
    -- 基本信息
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'direct', 'group'
    provider TEXT,  -- 'feishu', 'telegram', 'discord'
    
    -- 统计信息
    thread_count INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 线程表 (threads)
-- =============================================================================

CREATE TABLE IF NOT EXISTS threads (
    -- 主键
    thread_id TEXT PRIMARY KEY,
    
    -- 基本信息
    channel_id TEXT NOT NULL,
    title TEXT,
    agent_id TEXT,
    
    -- 状态
    status TEXT DEFAULT 'active',  -- 'active', 'archived', 'deleted'
    
    -- 统计信息
    message_count INTEGER DEFAULT 0,
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
    
    -- 索引
    INDEX idx_channel_id (channel_id)
);

-- =============================================================================
-- 审计日志表 (audit_logs)
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    -- 主键
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 基本信息
    user_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    
    -- 详情
    details TEXT,  -- JSON
    ip_address TEXT,
    user_agent TEXT,
    
    -- 时间戳
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_timestamp (timestamp)
);

-- =============================================================================
-- 系统配置表 (system_config)
-- =============================================================================

CREATE TABLE IF NOT EXISTS system_config (
    -- 主键
    key TEXT PRIMARY KEY,
    
    -- 配置值
    value TEXT,
    description TEXT,
    
    -- 元数据
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 触发器 (Triggers)
-- =============================================================================

-- 自动更新 updated_at 字段
CREATE TRIGGER IF NOT EXISTS update_sessions_timestamp
AFTER UPDATE ON sessions
BEGIN
    UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_key = NEW.session_key;
END;

CREATE TRIGGER IF NOT EXISTS update_tasks_timestamp
AFTER UPDATE ON tasks
BEGIN
    UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE task_id = NEW.task_id;
END;

CREATE TRIGGER IF NOT EXISTS update_channels_timestamp
AFTER UPDATE ON channels
BEGIN
    UPDATE channels SET updated_at = CURRENT_TIMESTAMP WHERE channel_id = NEW.channel_id;
END;

CREATE TRIGGER IF NOT EXISTS update_threads_timestamp
AFTER UPDATE ON threads
BEGIN
    UPDATE threads SET updated_at = CURRENT_TIMESTAMP WHERE thread_id = NEW.thread_id;
END;

-- =============================================================================
-- 视图 (Views)
-- =============================================================================

-- 活跃会话视图
CREATE VIEW IF NOT EXISTS active_sessions AS
SELECT
    session_key,
    agent_id,
    agent_type,
    state,
    message_count,
    task_count,
    last_activity
FROM sessions
WHERE state IN ('running', 'idle')
AND last_activity > datetime('now', '-1 hour');

-- 待处理任务视图
CREATE VIEW IF NOT EXISTS pending_tasks AS
SELECT
    task_id,
    session_key,
    title,
    description,
    skills,
    priority,
    created_at
FROM tasks
WHERE status = 'pending'
ORDER BY priority DESC, created_at ASC;

-- =============================================================================
-- 初始数据
-- =============================================================================

-- 插入默认配置
INSERT OR IGNORE INTO system_config (key, value, description) VALUES
    ('version', '1.0.0', 'Slock Server 版本'),
    ('max_message_length', '10000', '最大消息长度'),
    ('max_session_idle_time', '3600', '最大会话空闲时间（秒）'),
    ('task_claim_timeout', '300', '任务认领超时时间（秒）');

-- =============================================================================
-- 索引优化
-- =============================================================================

-- 复合索引
CREATE INDEX IF NOT EXISTS idx_messages_session_timestamp ON messages(session_key, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_status_priority ON tasks(status, priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_sessions_state_activity ON sessions(state, last_activity DESC);
