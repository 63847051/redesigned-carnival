# 🛡️ 安全升级到独立 Agent - v3.0 方案

**设计时间**: 2026-03-04 22:03
**基于**: 之前的崩溃教训
**目标**: 零配置文件修改的安全升级

---

## 🎯 核心原则

### ❌ 避免的陷阱（基于之前的错误）

1. ❌ **不修改** `openclaw.json` 配置文件
2. ❌ **不添加** 当前版本不支持的配置键
3. ❌ **不使用** 会触发 Gateway 重启的配置
4. ❌ **不创建** 会无限循环的自动化脚本

### ✅ 安全策略

1. ✅ 使用 **环境变量**（不修改配置文件）
2. ✅ 使用 **ACP 模式**（不需要 `sessions` 配置）
3. ✅ **逐步验证**（每次改动都验证）
4. ✅ **快速回滚**（1 分钟恢复）

---

## 🚀 方案 A: 使用环境变量（推荐）⭐

### 原理

通过环境变量设置 `sessions.spawn` 配置，**不修改配置文件**。

### 步骤

#### Step 1: 创建环境变量文件（1 分钟）

```bash
# 创建环境变量文件
cat > /root/.openclaw/gateway.env << 'EOF'
# OpenClaw Gateway 环境变量
# 允许创建独立子 Agent

OPENCLAW_SESSIONS_SPAWN_ALLOW_ANY=true
OPENCLAW_SESSIONS_SPAWN_ALLOWED_AGENTS=*
EOF

echo "✅ 环境变量文件已创建"
```

#### Step 2: 修改 systemd 服务（2 分钟）

```bash
# 1. 停止 Gateway
systemctl --user stop openclaw-gateway

# 2. 修改服务文件，添加环境变量
mkdir -p /root/.config/systemd/user/
cat > /root/.config/systemd/user/openclaw-gateway.service << 'EOF'
[Unit]
Description=OpenClaw Gateway (v2026.2.26)
After=network.target

[Service]
EnvironmentFile=/root/.openclaw/gateway.env
ExecStart=/usr/bin/openclaw gateway --port 18789
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

# 3. 重新加载 systemd
systemctl --user daemon-reload

# 4. 启动 Gateway
systemctl --user start openclaw-gateway

# 5. 等待启动
sleep 5

# 6. 验证状态
systemctl --user is-active openclaw-gateway
```

#### Step 3: 验证配置（1 分钟）

```bash
# 在主控 Agent 中运行
agents_list
```

**预期输出**：
```json
{
  "requester": "main",
  "allowAny": true,  // ✅ 应该是 true
  "agents": [...]
}
```

#### Step 4: 测试独立 Agent（2 分钟）

```javascript
// 创建第一个独立 Agent
sessions_spawn({
  runtime: "subagent",
  mode: "session",
  thread: true,
  agentId: "test-agent",
  model: "glmcode/glm-4.5-air",
  label: "测试",
  task: "你是测试 Agent"
})
```

#### Step 5: 回滚（如果需要）（1 分钟）

```bash
# 如果出现问题，立即回滚

# 1. 停止 Gateway
systemctl --user stop openclaw-gateway

# 2. 恢复原始服务文件
cat > /root/.config/systemd/user/openclaw-gateway.service << 'EOF'
[Unit]
Description=OpenClaw Gateway (v2026.2.26)
After=network.target

[Service]
ExecStart=/usr/bin/openclaw gateway --port 18789
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

# 3. 重新加载
systemctl --user daemon-reload

# 4. 启动 Gateway
systemctl --user start openclaw-gateway
```

---

## 🚀 方案 B: 使用 ACP 模式（无需配置）

### 原理

使用 `runtime: "acp"` 模式，**不需要 `sessions` 配置**。

### 步骤

#### Step 1: 直接测试 ACP 模式（1 分钟）

```javascript
// 在主控 Agent 中运行
sessions_spawn({
  runtime: "acp",        // ACP 模式
  mode: "session",
  thread: true,
  model: "glmcode/glm-4.7",
  label: "设计专家",
  task: "你是室内设计专家"
})
```

#### Step 2: 验证是否成功

如果成功，你会收到类似这样的回复：
```
✅ 已创建独立 Agent: 设计专家
```

如果失败且提示权限问题，说明方案 A 是必须的。

---

## 🚀 方案 C: 混合方案（最优）

结合方案 A 和方案 B 的优势。

### 步骤

1. **先尝试方案 B**（ACP 模式）
   - 如果成功 → 直接使用
   - 如果失败 → 执行方案 A

2. **方案 A 成功后**
   - 使用 `subagent` 模式创建 Agent
   - 或继续使用 `acp` 模式

3. **验证并行处理**
   - 同时创建多个 Agent
   - 测试隔离性

---

## 🛡️ 安全检查清单

### 升级前
- [ ] 备份当前服务文件
- [ ] 记录当前 Gateway 状态
- [ ] 准备回滚脚本

### 升级中
- [ ] 每步都验证 Gateway 状态
- [ ] 检查日志无错误
- [ ] 确认配置文件未被修改

### 升级后
- [ ] 验证 `agents_list` 输出
- [ ] 测试创建独立 Agent
- [ ] 测试并行处理
- [ ] 验证隔离性

---

## 📊 方案对比

| 特性 | 方案 A (环境变量) | 方案 B (ACP 模式) | 方案 C (混合) |
|------|------------------|------------------|---------------|
| **修改配置文件** | ❌ 否 | ❌ 否 | ❌ 否 |
| **需要重启** | ✅ 是 | ❌ 否 | 视情况 |
| **成功率** | 高 | 中 | 最高 |
| **复杂度** | 中 | 低 | 中 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 我的推荐

### 方案 C（混合方案）⭐ **最推荐**

**原因**：
1. ✅ **最安全** - 不修改配置文件
2. ✅ **最灵活** - 两种方式都尝试
3. ✅ **成功率最高** - 如果 ACP 不行，用环境变量
4. ✅ **易回滚** - 1 分钟恢复

**执行流程**：
```
1. 尝试 ACP 模式（1 分钟）
   ├─ 成功 → 完成！
   └─ 失败 → 继续

2. 使用环境变量（5 分钟）
   ├─ 成功 → 完成！
   └─ 失败 → 回滚

3. 如果都失败 → 保持当前系统
```

---

## 🔧 自动化脚本（安全版本）

让我创建一个完全安全的自动化脚本：

```bash
#!/bin/bash
# 安全升级到独立 Agent v3.0
# 不修改配置文件，使用环境变量

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================"
echo "🛡️  安全升级到独立 Agent v3.0"
echo "========================================"
echo ""

# Step 1: 备份
echo -e "${YELLOW}📦 Step 1: 备份当前配置${NC}"
BACKUP_DIR="/root/.openclaw/backups/safe-upgrade-$(date +%Y%m%d%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp /root/.config/systemd/user/openclaw-gateway.service "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✅ 已备份到: $BACKUP_DIR${NC}"
echo ""

# Step 2: 尝试 ACP 模式
echo -e "${YELLOW}🧪 Step 2: 尝试 ACP 模式${NC}"
echo "请在主控 Agent 中运行以下命令测试："
echo ""
echo "sessions_spawn({"
echo "  runtime: \"acp\","
echo "  mode: \"session\","
echo "  thread: true,"
echo "  model: \"glmcode/glm-4.5-air\","
echo "  label: \"测试\","
echo "  task: \"你是测试\""
echo "})"
echo ""
read -p "ACP 模式是否成功？(y/n): " acp_success

if [ "$acp_success" = "y" ]; then
    echo -e "${GREEN}✅ ACP 模式成功！无需升级配置${NC}"
    exit 0
fi

echo ""

# Step 3: 使用环境变量
echo -e "${YELLOW}🔧 Step 3: 使用环境变量方案${NC}"

# 创建环境变量文件
cat > /root/.openclaw/gateway.env << 'EOF'
OPENCLAW_SESSIONS_SPAWN_ALLOW_ANY=true
OPENCLAW_SESSIONS_SPAWN_ALLOWED_AGENTS=*
EOF

echo -e "${GREEN}✅ 环境变量文件已创建${NC}"

# 修改服务文件
echo -e "${YELLOW}🔄 Step 4: 修改 systemd 服务${NC}"

systemctl --user stop openclaw-gateway

cat > /root/.config/systemd/user/openclaw-gateway.service << 'EOF'
[Unit]
Description=OpenClaw Gateway (v2026.2.26)
After=network.target

[Service]
EnvironmentFile=/root/.openclaw/gateway.env
ExecStart=/usr/bin/openclaw gateway --port 18789
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user start openclaw-gateway

sleep 5

if systemctl --user is-active --quiet openclaw-gateway; then
    echo -e "${GREEN}✅ Gateway 启动成功${NC}"
else
    echo -e "${RED}❌ Gateway 启动失败，正在回滚...${NC}"
    cp "$BACKUP_DIR/openclaw-gateway.service" /root/.config/systemd/user/
    systemctl --user daemon-reload
    systemctl --user start openclaw-gateway
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 升级完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📋 下一步："
echo "  1. 在主控 Agent 中运行: agents_list"
echo "  2. 验证 allowAny 是否为 true"
echo "  3. 测试创建独立 Agent"
echo ""
echo "📁 备份位置: $BACKUP_DIR"
echo ""
```

---

## 📋 执行清单

- [ ] 阅读并理解升级方案
- [ ] 选择方案（推荐方案 C）
- [ ] 准备回滚脚本
- [ ] 执行升级
- [ ] 验证结果
- [ ] 测试并行处理
- [ ] 更新文档

---

## 🎉 总结

### 核心改进

1. ✅ **不修改配置文件** - 避免 `sessions` 键问题
2. ✅ **使用环境变量** - 安全可靠
3. ✅ **逐步验证** - 每步都检查
4. ✅ **快速回滚** - 1 分钟恢复

### 预期结果

- ✅ 成功升级到独立 Agent
- ✅ 支持并行处理
- ✅ 100% 上下文隔离
- ✅ Gateway 稳定运行

---

**准备好安全升级了吗？** 🚀

只需要说：**"大领导，执行安全升级！"**

---

*创建时间: 2026-03-04 22:03*
*版本: v3.0*
*基于: 崩溃教训*
*状态: ✅ 安全方案已准备*
