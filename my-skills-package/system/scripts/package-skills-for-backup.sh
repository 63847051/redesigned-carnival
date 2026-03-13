#!/bin/bash
# 技能系统打包脚本 - 用于备份和迁移

set -e

WORKSPACE="/root/.openclaw/workspace"
SKILLS_DIR="$WORKSPACE/skills"
PACKAGE_DIR="$WORKSPACE/my-skills-package"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 颜色定义
ECHO_GREEN='\033[0;32m'
ECHO_BLUE='\033[0;34m'
ECHO_YELLOW='\033[1;33m'
ECHO_NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

success() {
    echo -e "${ECHO_GREEN}✅ $1${ECHO_NC}"
}

info() {
    echo -e "${ECHO_BLUE}ℹ️  $1${ECHO_NC}"
}

warning() {
    echo -e "${ECHO_YELLOW}⚠️  $1${ECHO_NC}"
}

log "📦 开始打包技能系统..."
echo ""

# 1. 创建打包目录
info "创建打包目录..."
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"
success "打包目录创建完成: $PACKAGE_DIR"
echo ""

# 2. 复制所有技能
info "复制所有技能..."
cp -r "$SKILLS_DIR"/* "$PACKAGE_DIR/" 2>/dev/null || true
success "技能复制完成"
echo ""

# 3. 复制核心系统文件
info "复制核心系统文件..."
mkdir -p "$PACKAGE_DIR/system"

# 核心文档
cp "$WORKSPACE/SOUL.md" "$PACKAGE_DIR/system/" 2>/dev/null || true
cp "$WORKSPACE/IDENTITY.md" "$PACKAGE_DIR/system/" 2>/dev/null || true
cp "$WORKSPACE/USER.md" "$PACKAGE_DIR/system/" 2>/dev/null || true
cp "$WORKSPACE/AGENTS.md" "$PACKAGE_DIR/system/" 2>/dev/null || true
cp "$WORKSPACE/TOOLS.md" "$PACKAGE_DIR/system/" 2>/dev/null || true
cp "$WORKSPACE/HEARTBEAT.md" "$PACKAGE_DIR/system/" 2>/dev/null || true

# 学习系统
mkdir -p "$PACKAGE_DIR/system/learning"
cp -r "$WORKSPACE/.learnings" "$PACKAGE_DIR/system/learning/" 2>/dev/null || true

# 脚本
mkdir -p "$PACKAGE_DIR/system/scripts"
cp "$WORKSPACE"/scripts/*.sh "$PACKAGE_DIR/system/scripts/" 2>/dev/null || true

success "核心系统文件复制完成"
echo ""

# 4. 创建安装脚本
info "创建安装脚本..."
cat > "$PACKAGE_DIR/install.sh" << 'EOF'
#!/bin/bash
# 技能系统一键安装脚本

set -e

WORKSPACE="${WORKSPACE:-/root/.openclaw/workspace}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 安装技能系统到 $WORKSPACE"

# 1. 安装技能
echo "📋 安装技能..."
for skill_dir in "$SCRIPT_DIR"/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
        skill_name=$(basename "$skill_dir")
        if [ "$skill_name" != "system" ]; then
            echo "  安装: $skill_name"
            rm -rf "$WORKSPACE/skills/$skill_name"
            cp -r "$skill_dir" "$WORKSPACE/skills/"
        fi
    fi
done

# 2. 安装系统文件
echo "🔧 安装系统文件..."
cp -r "$SCRIPT_DIR/system/"* "$WORKSPACE/" 2>/dev/null || true

# 3. 设置执行权限
echo "⚙️  设置权限..."
chmod +x "$WORKSPACE"/scripts/*.sh 2>/dev/null || true

echo ""
echo "✅ 技能系统安装完成！"
echo ""
echo "📊 已安装技能："
ls -1 "$SCRIPT_DIR" | grep -v "^system$" | while read skill; do
    echo "  - $skill"
done
EOF

chmod +x "$PACKAGE_DIR/install.sh"
success "安装脚本创建完成"
echo ""

# 5. 创建 README
info "创建 README..."
cat > "$PACKAGE_DIR/README.md" << 'EOF'
# 我的技能系统包

**打包时间**: {TIMESTAMP}
**系统版本**: v5.10
**OpenClaw 版本**: 2026.2.26

---

## 📦 包含内容

### 技能列表
{SKILL_LIST}

### 系统文件
- `SOUL.md` - 系统核心
- `IDENTITY.md` - 身份定义
- `USER.md` - 用户信息
- `AGENTS.md` - Agent 配置
- `TOOLS.md` - 工具配置
- `HEARTBEAT.md` - 心跳检查

### 学习系统
- `.learnings/` - 设计模式、最佳实践、错误记录
- `scripts/` - 自动化脚本

---

## 🚀 一键安装

### 方式 1: 自动安装（推荐）

```bash
cd my-skills-package
bash install.sh
```

### 方式 2: 手动安装

```bash
# 1. 复制技能到工作区
cp -r */your-skill/* /root/.openclaw/workspace/skills/

# 2. 复制系统文件
cp -r system/* /root/.openclaw/workspace/

# 3. 设置权限
chmod +x /root/.openclaw/workspace/scripts/*.sh
```

---

## 📋 系统要求

- OpenClaw: 2026.2.26 或更高
- Node.js: v22.22.0
- 操作系统: Linux (OpenCloudOS, Ubuntu, etc.)

---

## 🎯 快速开始

安装后，重启 Gateway：

```bash
systemctl --user restart openclaw-gateway
```

---

## 📚 更多信息

- **OpenClaw 文档**: https://docs.openclaw.ai
- **社区**: https://discord.com/invite/clawd
- **技能市场**: https://clawhub.com

---

**打包人**: 大领导 🎯
**系统版本**: v5.10
**打包时间**: {TIMESTAMP}
EOF

success "README 创建完成"
echo ""

# 6. 生成统计信息
info "生成统计信息..."

SKILL_COUNT=$(ls -1 "$PACKAGE_DIR" | grep -v "^system$" | grep -v "^install.sh$" | grep -v "^README.md$" | wc -l)

sed -i "s/{TIMESTAMP}/$TIMESTAMP/g" "$PACKAGE_DIR/README.md"

# 生成技能列表
SKILL_LIST=""
for skill_dir in "$PACKAGE_DIR"/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
        skill_name=$(basename "$skill_dir")
        if [ "$skill_name" != "system" ]; then
            SKILL_LIST="$SKILL_LIST- $skill_name\n"
        fi
    fi
done

sed -i "s|{SKILL_LIST}|$SKILL_LIST|g" "$PACKAGE_DIR/README.md"

success "统计信息生成完成"
echo ""

# 7. 创建压缩包
info "创建压缩包..."
cd "$PACKAGE_DIR/.."
tar -czf "my-skills-package-$TIMESTAMP.tar.gz" "my-skills-package/"
success "压缩包创建完成"
echo ""

# 8. 输出报告
echo "======================================"
success "技能系统打包完成！"
echo "======================================"
echo ""
echo "📦 包位置: $PACKAGE_DIR"
echo "📊 技能数量: $SKILL_COUNT"
echo "🗜️  压缩包: my-skills-package-$TIMESTAMP.tar.gz"
echo ""
echo "📋 包含的技能:"
ls -1 "$PACKAGE_DIR" | grep -v "^system$" | grep -v "^install.sh$" | grep -v "^README.md$" | while read skill; do
    echo "  - $skill"
done
echo ""
echo "🚀 快速安装:"
echo "  cd $PACKAGE_DIR && bash install.sh"
echo ""
