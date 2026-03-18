/**
 * tasks-manager.js - 任务管理器
 * 
 * 功能: 管理共享任务列表
 */

const fs = require('fs');
const path = require('path');

// 配置
const TASKS_FILE = path.join(process.cwd(), '.claw/tasks/tasks.json');
const README_FILE = path.join(process.cwd(), '.claw/tasks/README.md');

// 加载任务
function loadTasks() {
  try {
    const content = fs.readFileSync(TASKS_FILE, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    return {
      version: '1.0.0',
      updated: new Date().toISOString(),
      tasks: []
    };
  }
}

// 保存任务
function saveTasks(data) {
  data.updated = new Date().toISOString();
  fs.writeFileSync(TASKS_FILE, JSON.stringify(data, null, 2));
  updateReadme(data);
}

// 更新 README
function updateReadme(data) {
  const todo = data.tasks.filter(t => t.status === 'todo');
  const inProgress = data.tasks.filter(t => t.status === 'in_progress');
  const done = data.tasks.filter(t => t.status === 'done');

  const content = `# 共享任务列表系统

**版本**: ${data.version}
**更新时间**: ${new Date().toLocaleString('zh-CN', {timeZone: 'Asia/Shanghai'})}

---

## 📋 任务列表

### 待办任务（Todo）
${todo.length === 0 ? '- 无待办任务 ✅' : todo.map(t => `- [ ] ${t.title} (${t.assignee})`).join('\n')}

### 进行中（In Progress）
${inProgress.length === 0 ? '- 无进行中任务 ✅' : inProgress.map(t => `- [🔄] ${t.title} (${t.assignee})`).join('\n')}

### 已完成（Done）
${done.length === 0 ? '- 无已完成任务' : done.map(t => `- [✅] ${t.title} (${t.assignee}) - ${t.completed_at}`).join('\n')}

---

## 🎯 任务状态说明

**待办（Todo）**: 计划中，未开始
**进行中（In Progress）**: 正在执行
**已完成（Done）**: 已完成

---

## 📊 任务统计

- **总任务**: ${data.tasks.length} 个
- **已完成**: ${done.length} 个 ✅
- **进行中**: ${inProgress.length} 个
- **待办**: ${todo.length} 个

---

## 🔗 依赖关系
${data.tasks.filter(t => t.dependencies && t.dependencies.length > 0).length === 0 ? '无复杂依赖关系 ✅' : '存在任务依赖关系'}

---

*更新时间: ${new Date().toLocaleString('zh-CN', {timeZone: 'Asia/Shanghai'})*
*系统状态: ${inProgress.length > 0 ? '\\u{1F504} 进行中' : '\\u2705 任务全部完成'}*
`;

  fs.writeFileSync(README_FILE, content);
}

// 添加任务
function addTask(title, description, priority, assignee, dependencies = []) {
  const data = loadTasks();
  
  const task = {
    id: `task-${Date.now()}`,
    title,
    description,
    priority: priority || 'P1', // P0, P1, P2, P3
    assignee,
    status: 'todo',
    dependencies,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };
  
  data.tasks.push(task);
  saveTasks(data);
  
  console.log(`✅ 任务已添加: ${task.title}`);
  return task;
}

// 更新任务状态
function updateTaskStatus(taskId, status) {
  const data = loadTasks();
  const task = data.tasks.find(t => t.id === taskId);
  
  if (!task) {
    console.log(`❌ 任务未找到: ${taskId}`);
    return null;
  }
  
  task.status = status;
  task.updated_at = new Date().toISOString();
  
  if (status === 'done') {
    task.completed_at = new Date().toISOString();
  }
  
  saveTasks(data);
  console.log(`✅ 任务状态已更新: ${task.title} → ${status}`);
  
  return task;
}

// 列出任务
function listTasks(status = null) {
  const data = loadTasks();
  let tasks = data.tasks;
  
  if (status) {
    tasks = tasks.filter(t => t.status === status);
  }
  
  console.log(`\n📋 任务列表 (${tasks.length} 个):\n`);
  
  tasks.forEach((task, index) => {
    const statusIcon = {
      'todo': '⏳',
      'in_progress': '🔄',
      'done': '✅'
    }[task.status] || '❓';
    
    console.log(`${index + 1}. ${statusIcon} [${task.priority}] ${task.title}`);
    console.log(`   负责人: ${task.assignee}`);
    console.log(`   状态: ${task.status}`);
    console.log(`   创建: ${new Date(task.created_at).toLocaleString('zh-CN', {timeZone: 'Asia/Shanghai'})}`);
    if (task.description) {
      console.log(`   描述: ${task.description}`);
    }
    console.log('');
  });
  
  return tasks;
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'add':
      addTask(
        args[1], // title
        args[2], // description
        args[3], // priority
        args[4] || '主控 Agent', // assignee
        args[5] ? args[5].split(',') : [] // dependencies
      );
      break;
      
    case 'update':
      updateTaskStatus(args[1], args[2]);
      break;
      
    case 'list':
      listTasks(args[1]);
      break;
      
    case 'todo':
      listTasks('todo');
      break;
      
    case 'in-progress':
      listTasks('in_progress');
      break;
      
    case 'done':
      listTasks('done');
      break;
      
    default:
      console.log(`
📋 任务管理器

用法:
  node tasks-manager.js add <title> <description> <priority> <assignee>
  node tasks-manager.js update <task-id> <status>
  node tasks-manager.js list [status]
  node tasks-manager.js todo
  node tasks-manager.js in-progress
  node tasks-manager.js done

示例:
  node tasks-manager.js add "优化DP-006" "扩展上下文边界" "P1" "主控 Agent"
  node tasks-manager.js update task-123 in_progress
  node tasks-manager.js list
      `);
  }
}

// 运行
if (require.main === module) {
  main();
}

module.exports = {
  addTask,
  updateTaskStatus,
  listTasks,
  loadTasks
};
