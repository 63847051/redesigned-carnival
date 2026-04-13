# OpenClaw 版本检查历史

**更新时间**: 2026-04-12T00:14:36Z

---

## 📅 检查记录

### 2026-04-12T00:14:36Z

**检查方式**: web_fetch (GitHub API)
**最新版本**: 2026.4.11-beta.1 (Pre-release)
**稳定版本**: 2026.4.10

#### 新版本特性: 2026.4.11-beta.1

**发布时间**: 2026-04-11T15:15:03Z

##### 主要更新 (Changes)

1. **Dreaming/Memory Wiki 增强**
   - 新增 ChatGPT 导入功能
   - 新增"Imported Insights"和"Memory Palace"日记子标签
   - Dreaming 可以直接从 UI 检查导入的源聊天、编译的 wiki 页面和完整源页面

2. **Control UI/Webchat 改进**
   - 渲染助手媒体/回复/语音指令为结构化聊天气泡
   - 新增 `[embed ...]` 富输出标签
   - 外部嵌入 URL 需要配置门控

3. **视频生成工具增强** ⭐
   - URL-only 资产生交付
   - 类型化 `providerOptions`
   - 参考音频输入
   - 每资产角色提示
   - 自适应宽高比支持
   - 更高的图像输入上限
   - 视频提供商可以暴露更丰富的生成模式，而无需将大文件强制加载到内存中

4. **Feishu 改进**
   - 改进文档评论会话
   - 更丰富的上下文解析
   - 评论反应和打字反馈
   - 文档线程对话行为更像聊天对话

5. **Microsoft Teams 增强**
   - 新增反应支持
   - 反应列表
   - Graph 分页
   - 委托 OAuth 设置
   - 在保留应用认证读取路径的同时发送反应

6. **插件系统增强**
   - 允许插件清单声明激活和设置描述符
   - 插件设置流程可以描述所需的认证、配对和配置步骤
   - 无需核心硬编码特殊情况

7. **Ollama 性能优化** ⭐
   - 在模型发现期间缓存 `/api/show` 上下文窗口和功能元数据
   - 重复的选择器刷新停止重新获取未更改的模型
   - 空响应后仍重试
   - 摘要更改时失效

8. **模型/提供商诊断改进** ⭐
   - 在嵌入式代理调试日志中显示配置的 OpenAI 兼容端点的分类方式
   - 本地和代理路由问题更容易诊断

9. **QA/Parity 增强**
   - 新增 GPT-5.4 vs Opus 4.6 代理奇偶校验报告门控
   - 共享场景覆盖检查
   - 更严格的证据启发式
   - 跳过场景核算以进行维护者审查

##### Bug 修复 (Fixes)

1. **OpenAI/Codex OAuth 修复** 🔴 CRITICAL
   - 停止重写上游授权 URL 范围
   - 新的 Codex 登录不会在返回授权代码之前因 `invalid_scope` 而失败

2. **音频转录修复** 🔴 CRITICAL
   - 仅对 OpenAI 兼容的多部分请求禁用固定 DNS
   - 仍验证主机名
   - OpenAI、Groq 和 Mistral 转录再次工作，而不削弱其他请求路径

3. **macOS/Talk Mode 修复**
   - 首次启用时授予麦克风权限后，继续启动 Talk Mode
   - 不需要第二次切换

4. **Control UI/Webchat 修复**
   - 将代理运行 TTS 音频回复持久化到 webchat 历史记录
   - 保留交错工具卡配对
   - 生成的音频和混合工具输出保持附加到正确的消息

5. **WhatsApp 修复**
   - 在没有显式帐户 ID 的情况下使用活动侦听器助手时，遵守配置的默认帐户
   - 命名的默认帐户不会注册为 `default`

6. **CP/Agents 修复**
   - 在 ACP 父流更新中抑制评论阶段子助手中继文本
   - 生成的子运行停止将内部进度聊天泄漏到父会话

7. **Agents/Timeouts 修复** 🔴 IMPORTANT
   - 在 LLM 空闲监视器中遵守显式运行超时
   - 对齐默认超时配置
   - 慢速模型可以继续工作直到配置的限制，而不是使用错误的空闲窗口

8. **Config 修复**
   - 在生成的 zod 架构中包含 `asyncCompletion`
   - 记录的异步完成配置不再因无法识别的密钥错误而失败

9. **Google/Veo 修复**
   - 停止发送不支持的 `numberOfVideos` 请求字段
   - Gemini Developer API Veo 运行不会在 OpenClaw 完成预期的 Google 视频生成路径之前失败

10. **QA/Packaging 修复** 🔴 IMPORTANT
    - 停止打包的 CLI 启动和完成缓存生成读取仅限仓库的 QA 场景 markdown
    - 在 npm 版本中发布捆绑的 QA 场景包
    - 即使 QA 设置被破坏，`openclaw completion --write-state` 也能正常工作

11. **Codex/QA 修复**
    - 将 Codex 应用服务器协调聊天保留在可见回复之外
    - 添加实时 QA 泄漏场景
    - 将泄漏的护罩元文本分类为 QA 失败而不是成功的回复

12. **WhatsApp 修复**
    - 通过网关拥有的操作路径路由 `message react`
    - 反应在 DM 和群组聊天中都使用实时 WhatsApp 侦听器
    - 匹配 `message send` 和 `message poll`

---

## 📊 版本对比

### 2026.4.11-beta.1 vs 2026.4.10

| 特性 | 2026.4.10 | 2026.4.11-beta.1 |
|------|-----------|------------------|
| Dreaming/Memory Wiki | 基础功能 | ChatGPT 导入 + UI 增强 |
| Video Generate | 基础功能 | URL-only 交付 + 自适应宽高比 |
| Feishu | 基础功能 | 文档评论增强 |
| Microsoft Teams | 基础功能 | 反应支持 + Graph 分页 |
| Plugin System | 硬编码 | 声明式激活和设置 |
| Ollama | 每次重新获取 | 缓存优化 ⭐ |
| Models/Providers | 基础日志 | 增强诊断 ⭐ |
| OpenAI/Codex OAuth | ❌ 范围重写问题 | ✅ 已修复 🔴 |
| Audio Transcription | ❌ DNS 问题 | ✅ 已修复 🔴 |
| Agents/Timeouts | ⚠️ 错误的空闲窗口 | ✅ 已修复 🔴 |

---

## 🚨 Breaking Changes

**无重大破坏性变更** (Pre-release 版本)

---

## 🎯 建议操作

### 对于当前用户 (2026.4.10)

1. **等待稳定版本**
   - 2026.4.11-beta.1 是预发布版本
   - 建议等待正式稳定版

2. **关注关键修复**
   - 🔴 OpenAI/Codex OAuth 修复
   - 🔴 音频转录修复
   - 🔴 Agents/Timeouts 修复

3. **性能优化**
   - Ollama 缓存优化（如果使用 Ollama）
   - 模型/提供商诊断改进

### 升级准备

```bash
# 检查当前版本
openclaw --version

# 升级前备份
bash /root/.openclaw/workspace/scripts/complete-backup.sh

# 等待正式版发布
npm install -g openclaw@latest
```

---

**下次检查**: 2026-04-13T00:14:36Z (24小时后)

