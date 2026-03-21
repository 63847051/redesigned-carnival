#!/usr/bin/env node

/**
 * HeyCube 个人档案管理 CLI 工具
 * 用于管理本地 SQLite 档案库
 */

const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

// 数据库路径配置
const DB_PATH = process.env.HAICUBE_DB_PATH || path.join(process.env.HOME || '', '.openclaw', 'workspace', 'personal-db.sqlite');

// 初始化数据库连接
let db;

function initDB() {
  const dbDir = path.dirname(DB_PATH);
  if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
  }
  
  db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL');
  
  // 创建表结构
  db.exec(`
    CREATE TABLE IF NOT EXISTS personal_profiles (
      dimension_id TEXT PRIMARY KEY,
      dimension_name TEXT NOT NULL,
      value TEXT,
      value_type TEXT DEFAULT 'string',
      updated_at INTEGER NOT NULL,
      created_at INTEGER NOT NULL
    );
    
    CREATE INDEX IF NOT EXISTS idx_dimension_id ON personal_profiles(dimension_id);
    CREATE INDEX IF NOT EXISTS idx_updated_at ON personal_profiles(updated_at);
  `);
  
  console.log(`✅ 数据库已初始化: ${DB_PATH}`);
}

// 获取单个维度
function getDimension(dimensionId) {
  const stmt = db.prepare('SELECT * FROM personal_profiles WHERE dimension_id = ?');
  const result = stmt.get(dimensionId);
  return result;
}

// 批量获取维度
function getBatchDimensions(dimensionIds) {
  const placeholders = dimensionIds.map(() => '?').join(',');
  const stmt = db.prepare(`SELECT * FROM personal_profiles WHERE dimension_id IN (${placeholders})`);
  const results = stmt.all(...dimensionIds);
  return results;
}

// 设置单个维度
function setDimension(dimensionId, dimensionName, value, valueType = 'string') {
  const now = Date.now();
  const stmt = db.prepare(`
    INSERT INTO personal_profiles (dimension_id, dimension_name, value, value_type, updated_at, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(dimension_id) DO UPDATE SET
      dimension_name = excluded.dimension_name,
      value = excluded.value,
      value_type = excluded.value_type,
      updated_at = excluded.updated_at
  `);
  
  stmt.run(dimensionId, dimensionName, value, valueType, now, now);
  console.log(`✅ 已设置维度: ${dimensionId} = ${value}`);
}

// 批量设置维度
function setBatchDimensions(data) {
  const now = Date.now();
  const stmt = db.prepare(`
    INSERT INTO personal_profiles (dimension_id, dimension_name, value, value_type, updated_at, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(dimension_id) DO UPDATE SET
      dimension_name = excluded.dimension_name,
      value = excluded.value,
      value_type = excluded.value_type,
      updated_at = excluded.updated_at
  `);
  
  const transaction = db.transaction((data) => {
    for (const [dimensionId, value] of Object.entries(data)) {
      const dimensionName = dimensionId.split('.').pop();
      stmt.run(dimensionId, dimensionName, value, 'string', now, now);
    }
  });
  
  transaction(data);
  console.log(`✅ 已批量设置 ${Object.keys(data).length} 个维度`);
}

// 删除维度
function deleteDimension(dimensionId) {
  const stmt = db.prepare('DELETE FROM personal_profiles WHERE dimension_id = ?');
  const result = stmt.run(dimensionId);
  if (result.changes > 0) {
    console.log(`✅ 已删除维度: ${dimensionId}`);
  } else {
    console.log(`⚠️  维度不存在: ${dimensionId}`);
  }
}

// 列出所有维度
function listAllDimensions() {
  const stmt = db.prepare('SELECT * FROM personal_profiles ORDER BY updated_at DESC');
  const results = stmt.all();
  console.log(`\n📊 共有 ${results.length} 个维度:\n`);
  results.forEach((row, i) => {
    console.log(`${i + 1}. ${row.dimension_id}`);
    console.log(`   名称: ${row.dimension_name}`);
    console.log(`   值: ${row.value}`);
    console.log(`   更新时间: ${new Date(row.updated_at).toLocaleString('zh-CN')}`);
    console.log();
  });
}

// 导出为 JSON
function exportJSON() {
  const stmt = db.prepare('SELECT * FROM personal_profiles');
  const results = stmt.all();
  const exportPath = path.join(path.dirname(DB_PATH), 'personal-db-export.json');
  fs.writeFileSync(exportPath, JSON.stringify(results, null, 2));
  console.log(`✅ 已导出到: ${exportPath}`);
}

// CLI 命令行接口
const command = process.argv[2];
const args = process.argv.slice(3);

try {
  initDB();
  
  switch (command) {
    case 'get':
      if (args.length === 0) {
        console.log('用法: node personal-db.js get <dimension_id>');
        process.exit(1);
      }
      const result = getDimension(args[0]);
      if (result) {
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.log('⚠️  维度不存在');
      }
      break;
      
    case 'get-batch':
      if (args.length === 0) {
        console.log('用法: node personal-db.js get-batch <dimension_id1,dimension_id2,...>');
        process.exit(1);
      }
      const ids = args[0].split(',');
      const results = getBatchDimensions(ids);
      console.log(JSON.stringify(results, null, 2));
      break;
      
    case 'set':
      if (args.length < 3) {
        console.log('用法: node personal-db.js set <dimension_id> <dimension_name> <value>');
        process.exit(1);
      }
      setDimension(args[0], args[1], args[2]);
      break;
      
    case 'set-batch':
      if (args.length === 0) {
        console.log('用法: node personal-db.js set-batch \'{"dim1": "value1", "dim2": "value2"}\'');
        process.exit(1);
      }
      const data = JSON.parse(args[0]);
      setBatchDimensions(data);
      break;
      
    case 'delete':
      if (args.length === 0) {
        console.log('用法: node personal-db.js delete <dimension_id>');
        process.exit(1);
      }
      deleteDimension(args[0]);
      break;
      
    case 'list':
      listAllDimensions();
      break;
      
    case 'export':
      exportJSON();
      break;
      
    default:
      console.log(`
HeyCube 个人档案管理工具

用法:
  node personal-db.js <command> [args]

命令:
  get <dimension_id>                    获取单个维度
  get-batch <dimension_id1,id2,...>     批量获取维度
  set <dimension_id> <name> <value>     设置单个维度
  set-batch '{"dim": "value"}'          批量设置维度
  delete <dimension_id>                 删除维度
  list                                  列出所有维度
  export                                导出为 JSON

示例:
  node personal-db.js get profile.career
  node personal-db.js get-batch "profile.career,behavior.work_habits"
  node personal-db.js set profile.career.career_stage "职业阶段" "资深"
  node personal-db.js set-batch '{"profile.career": "软件工程师", "behavior.work_habits.time_management": "番茄工作法"}'
  node personal-db.js list
  node personal-db.js export
      `);
  }
  
  db.close();
} catch (error) {
  console.error('❌ 错误:', error.message);
  process.exit(1);
}
