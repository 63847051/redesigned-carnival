# 飞书工作日志 Skill - 详细需求文档

**版本**: 1.0
**日期**: 2026-03-15
**开发者**: OpenCode (minimax-m2.5-free 免费模型)

---

## 📋 项目概述

**目标**: 创建一个智能飞书工作日志管理 skill

**核心功能**:
1. 自然语言记录工作日志
2. 智能意图识别和参数推断
3. 飞书多维表格集成
4. 统计和报告生成

---

## 🏗️ 核心模块需求

### 模块 1: BitableManager

**功能**: 飞书多维表格 API 管理

**需求**:
```python
class BitableManager:
    """飞书多维表格管理器"""
    
    def __init__(self, app_token: str, table_id: str):
        """
        初始化
        
        参数:
            app_token: Bitable app token (BISAbNgYXa7Do1sc36YcBChInnS)
            table_id: Table ID (tbl5s8TEZ0tKhEm7)
        """
        pass
    
    def add_record(self, content: str, project_type: str, 
                   priority: str, status: str, note: str = "") -> Dict:
        """
        添加记录
        
        参数:
            content: 任务内容
            project_type: 项目类型（室内设计、技术开发、文档编写）
            priority: 优先级（高、中、低）
            status: 状态（待确认、进行中、已完成）
            note: 备注（可选）
        
        返回:
            Dict: 创建的记录信息
        """
        pass
    
    def query_records(self, filters: Dict = None) -> List[Dict]:
        """
        查询记录
        
        参数:
            filters: 筛选条件
                - status: 状态筛选
                - project_type: 项目类型筛选
                - date_range: 日期范围
        
        返回:
            List[Dict]: 记录列表
        """
        pass
    
    def update_status(self, record_id: str, status: str) -> bool:
        """
        更新状态
        
        参数:
            record_id: 记录 ID
            status: 新状态
        
        返回:
            bool: 是否成功
        """
        pass
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        
        返回:
            Dict: 
                - total: 总任务数
                - completed: 完成数
                - in_progress: 进行中
                - pending: 待确认
                - completion_rate: 完成率
        """
        pass
```

**技术要求**:
- 使用现有的 `feishu_bitable_*` 工具
- 错误处理完整
- 类型提示完整
- 日志记录

---

### 模块 2: IntentAnalyzer

**功能**: 智能意图分析和参数提取

**需求**:
```python
class IntentAnalyzer:
    """意图分析器"""
    
    # 意图类型
    INTENTS = {
        'record': ['记录', '添加', '新建', '创建', '写下'],
        'query': ['查询', '查看', '显示', '统计', '多少'],
        'update': ['更新', '修改', '标记', '完成'],
        'delete': ['删除', '移除'],
    }
    
    # 项目类型关键词
    PROJECT_KEYWORDS = {
        '室内设计': ['设计', '图纸', '平面图', '立面图', '天花', '排砖'],
        '技术开发': ['代码', '开发', '爬虫', 'API', '脚本', '前端'],
        '文档编写': ['文档', '手册', '说明', '报告'],
    }
    
    # 优先级关键词
    PRIORITY_KEYWORDS = {
        '高': ['紧急', '重要', '优先', '高'],
        '中': ['普通', '中', '正常'],
        '低': ['低', '不急', '稍后'],
    }
    
    # 状态关键词
    STATUS_KEYWORDS = {
        '待确认': ['待确认', '待办', 'todo'],
        '进行中': ['进行中', 'doing', '正在', '在做'],
        '已完成': ['完成', 'done', '已完成', '做好了'],
    }
    
    def analyze(self, text: str) -> Dict:
        """
        分析用户输入
        
        参数:
            text: 用户输入文本
        
        返回:
            Dict:
                - intent: 意图类型
                - content: 任务内容
                - project_type: 项目类型
                - priority: 优先级
                - status: 状态
                - note: 备注
        """
        pass
    
    def _detect_intent(self, text: str) -> str:
        """检测意图"""
        pass
    
    def _detect_project_type(self, text: str) -> str:
        """检测项目类型"""
        pass
    
    def _detect_priority(self, text: str) -> str:
        """检测优先级"""
        pass
    
    def _detect_status(self, text: str) -> str:
        """检测状态"""
        pass
```

**技术要求**:
- 关键词匹配算法
- 简单正则表达式
- 默认值处理
- 准确率 > 85%

---

### 模块 3: WorklogAssistant

**功能**: 主控制器，整合所有功能

**需求**:
```python
class WorklogAssistant:
    """工作日志智能助手"""
    
    def __init__(self, app_token: str, table_id: str):
        """
        初始化
        
        参数:
            app_token: Bitable app token
            table_id: Table ID
        """
        self.bitable_manager = BitableManager(app_token, table_id)
        self.intent_analyzer = IntentAnalyzer()
    
    def process(self, user_input: str) -> str:
        """
        处理用户输入
        
        参数:
            user_input: 用户输入
        
        返回:
            str: 处理结果
        """
        pass
    
    def _handle_record(self, params: Dict) -> str:
        """处理记录意图"""
        pass
    
    def _handle_query(self, params: Dict) -> str:
        """处理查询意图"""
        pass
    
    def _handle_update(self, params: Dict) -> str:
        """处理更新意图"""
        pass
```

**技术要求**:
- 清晰的控制流
- 完整的错误处理
- 友好的输出格式
- 日志记录

---

## 📝 使用场景

### 场景 1: 记录任务

**输入**: "记录一下：完成了3F会议室平面图设计"
**预期输出**:
- intent: record
- content: "完成了3F会议室平面图设计"
- project_type: "室内设计"
- status: "已完成"
- priority: "中"（默认）

### 场景 2: 查询统计

**输入**: "今天完成了多少任务？"
**预期输出**:
- intent: query
- filters: {status: "已完成", date: "今天"}
- 结果: "今天完成了 3 个任务"

### 场景 3: 更新状态

**输入**: "把第一个待办任务标记为完成"
**预期输出**:
- intent: update
- record_id: 第一个待办任务
- status: "已完成"

---

## 🔧 技术约束

1. **Python 版本**: 3.6+
2. **类型提示**: 必须 100% 覆盖
3. **文档字符串**: 所有公共方法
4. **错误处理**: 完整的异常处理
5. **日志记录**: 使用 logging 模块
6. **测试覆盖**: > 80%

---

## 📦 交付物

1. **bitable_manager.py** - Bitable 管理器
2. **intent_analyzer.py** - 意图分析器
3. **worklog_assistant.py** - 主控制器
4. **测试文件** - 单元测试

---

## ⚠️ 重要提示

1. **使用现有工具**: 
   - feishu_bitable_create_record
   - feishu_bitable_list_records
   - feishu_bitable_update_record

2. **Bitable 配置**:
   - app_token: BISAbNgYXa7Do1sc36YcBChInnS
   - table_id: tbl5s8TEZ0tKhEm7

3. **字段映射**:
   - content (内容)
   - project_type (项目类型)
   - priority (优先级别)
   - status (项目状态)
   - note (备注)

4. **默认值**:
   - project_type: "技术开发"（默认）
   - priority: "中"（默认）
   - status: "待确认"（默认）

---

**请按照以上需求编写代码，确保代码质量和可维护性！**
