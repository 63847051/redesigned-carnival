# 最佳实践 v1.0

**更新时间**: 2026-03-13 19:52
**来源**: 今日工作经验总结

---

## 🎯 微信文章读取

### 场景与工具选择

根据不同需求选择合适的工具：

| 场景 | 推荐工具 | 原因 |
|------|----------|------|
| **快速读取内容** | wechat-article-reader | Python 实现，快速轻量 |
| **需要截图** | wxmp-reader | 浏览器自动化，支持截图 |
| **完整分析** | wechat-reader | 功能最全，支持多种操作 |

### 实施步骤

#### 1. 安装工具
```bash
# 方式 1: 使用 skillhub（推荐）
skillhub install wechat-article-reader

# 方式 2: 手动安装
cd /root/.openclaw/workspace/skills
# 克隆或下载相应技能
```

#### 2. 使用示例
```bash
# 快速导出为 Markdown
python3 /root/.openclaw/workspace/skills/wechat-article-reader/scripts/export.py "https://mp.weixin.qq.com/s/XXXXX"

# 使用 wxmp-reader（带截图）
cd /root/.openclaw/workspace/skills/wxmp-reader
node scripts/fetch_wechat.js "https://mp.weixin.qq.com/s/XXXXX" --json
```

#### 3. 注意事项
- wxmp-reader 需要 Chromium，首次使用需安装依赖
- 文章会自动保存到工作目录的 source 文件夹
- 截图功能可选，失败不影响文本获取

---

## 🚀 项目安装流程

### 标准化流程

适用于大多数 Node.js 项目的安装：

```bash
# 1. 克隆仓库
cd /root/.openclaw/workspace
git clone <repository-url>

# 2. 进入项目目录
cd <project-name>

# 3. 安装依赖
npm install

# 4. 创建配置
cp config.json.example config.json
vim config.json

# 5. 测试启动
npm start

# 6. 生成文档（可选）
# 创建安装报告和快速开始指南
```

### 关键要点

1. **先验证，后配置**
   - 语法检查：`node -c server.js`
   - 配置测试：运行测试脚本（如果有）

2. **最小配置原则**
   - 只配置必要的部分
   - 其他功能可以后续添加

3. **日志管理**
   - 确保日志目录存在
   - 配置合理的日志级别

---

## 🎛️ Dashboard 管理

### 启动与管理

#### 启动服务
```bash
cd /root/.openclaw/workspace/ai-team-dashboard/dashboard

# 方式 1: 带日志记录（推荐）
./start-with-log.sh

# 方式 2: 直接启动
npm start
```

#### 监控日志
```bash
# 实时监控所有日志
./monitor-logs.sh

# 只看 API 请求
./monitor-logs.sh --api

# 只看性能统计
./monitor-logs.sh --perf

# 只看错误
./monitor-logs.sh --error
```

#### 生成分析报告
```bash
./analyze-logs.sh
```

#### 停止服务
```bash
./stop-dashboard.sh
```

### 配置建议

#### 最小配置（快速测试）
```json
{
  "dashboard": {
    "port": 3800,
    "logging": {
      "enabled": true,
      "level": "INFO",
      "file": true,
      "console": true
    }
  }
}
```

#### 生产配置
```json
{
  "dashboard": {
    "port": 3800,
    "logging": {
      "enabled": true,
      "level": "WARN",  // 降低日志级别
      "file": true,
      "console": false  // 关闭控制台输出
    }
  }
}
```

---

## 🧠 进化学习系统

### 使用时机

- ✅ 每日定时执行（建议）
- ✅ 完成重要任务后
- ✅ 遇到错误时
- ✅ 系统优化前

### 执行方式

```bash
# 完整进化系统
bash /root/.openclaw/workspace/scripts/self-evolution-system.sh

# 快速进化（只执行核心部分）
bash /root/.openclaw/workspace/scripts/heartbeat-evolution.sh
```

### 输出内容

1. **L7 配置验证** - 检查 API Key 格式
2. **6 层防护检测** - 确保系统安全
3. **错误检测** - 发现并记录最近错误
4. **PAI 深度学习** - 三层记忆管理
5. **超级大脑进化** - 自动优化决策
6. **知识存储** - 永久化学习成果

### 查看结果

```bash
# 查看最新进化报告
ls -lt /root/.openclaw/workspace/.learnings/evolution_report_*.md | head -1

# 查看 PAI 学习信号
cat /root/.openclaw/workspace/.pai-learning/signals/$(date +%Y-%m-%d)-signals.jsonl
```

---

## 🛠️ 技能管理

### 发现技能

```bash
# 使用 skillhub 搜索（推荐）
skillhub search "关键词"

# 使用 clawhub 搜索
clawhub search "关键词"
```

### 安装技能

```bash
# 使用 skillhub
skillhub install <skill-name>

# 使用 clawhub
clawhub install <skill-name>
```

### 管理技能

```bash
# 列出已安装技能
clawhub list

# 更新所有技能
clawhub update --all

# 更新特定技能
clawhub update <skill-name>
```

---

## 📝 文档编写

### 文档类型

1. **安装报告** (INSTALLATION_REPORT.md)
   - 安装步骤
   - 配置说明
   - 验证结果
   - 下一步操作

2. **快速开始** (QUICK_START.md)
   - 最小配置
   - 启动命令
   - 访问地址
   - 常见问题

3. **最佳实践** (BEST_PRACTICES.md)
   - 工作流程
   - 经验总结
   - 注意事项
   - 优化建议

### 编写原则

1. **结构清晰**
   - 使用标题层级
   - 添加目录
   - 分节说明

2. **示例完整**
   - 提供可执行的命令
   - 包含预期输出
   - 注释关键步骤

3. **持续更新**
   - 记录新经验
   - 修正错误
   - 优化流程

---

## 🔧 故障排查

### 常见问题

#### 问题 1: 端口被占用
```bash
# 检查端口占用
netstat -tlnp | grep :端口号

# 杀死占用进程
kill -9 <PID>
```

#### 问题 2: 依赖安装失败
```bash
# 清除缓存重新安装
npm cache clean --force
rm -rf node_modules
npm install
```

#### 问题 3: 权限问题
```bash
# 添加执行权限
chmod +x *.sh

# 修改文件所有者
chown -R user:group /path/to/project
```

#### 问题 4: 配置文件错误
```bash
# 验证 JSON 格式
python3 -m json.tool config.json

# 检查语法
node -c server.js
```

---

## 🎯 效率提升

### 批量操作

```bash
# 批量重命名
for file in *.txt; do mv "$file" "${file%.txt}.md"; done

# 批量转换
for file in *.png; do convert "$file" "${file%.png}.jpg"; done
```

### 快速导航

```bash
# 创建项目快捷方式
alias ai-dashboard="cd /root/.openclaw/workspace/ai-team-dashboard/dashboard"
alias workspace="cd /root/.openclaw/workspace"

# 添加到 ~/.bashrc
echo 'alias ai-dashboard="cd /root/.openclaw/workspace/ai-team-dashboard/dashboard"' >> ~/.bashrc
source ~/.bashrc
```

### 历史记录

```bash
# 查看最近执行的命令
history | tail -20

# 搜索历史
history | grep "关键词"

# 重复执行上一条命令
!!
```

---

## 📊 监控与维护

### 系统监控

```bash
# 检查内存使用
free -h

# 检查磁盘使用
df -h

# 检查进程
ps aux | grep node

# 检查端口
netstat -tlnp
```

### 日志管理

```bash
# 查看最新日志
tail -f /path/to/log

# 查找错误
grep ERROR /path/to/log

# 统计日志
wc -l /path/to/log
```

### 定期维护

```bash
# 清理日志文件
find /path/to/logs -name "*.log" -mtime +7 -delete

# 更新系统
yum update -y

# 清理缓存
npm cache clean --force
```

---

## 💡 经验总结

### 成功经验

1. **最小配置原则**
   - 不需要配置所有功能就能启动
   - 核心功能优先，附加功能后续添加

2. **文档先行**
   - 先编写文档，再执行操作
   - 记录每一步，方便回溯

3. **多方案备份**
   - 准备多个工具，形成互补
   - 不同场景使用不同方案

4. **自动化优先**
   - 能自动化的就不要手动
   - 使用脚本替代重复操作

### 避免的陷阱

1. **过度配置**
   - 不要一开始就配置所有功能
   - 先让系统跑起来

2. **忽略日志**
   - 及时查看日志
   - 错误信息很重要

3. **缺乏备份**
   - 配置文件要备份
   - 重要数据要备份

---

**版本**: v1.0
**最后更新**: 2026-03-13
**维护者**: 大领导 🎯

---

*持续积累，持续改进！* 📚✨
