#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HeyCube 个人档案管理 CLI 工具
用于管理本地 SQLite 档案库
"""

import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 数据库路径配置
DB_PATH = os.environ.get('HAICUBE_DB_PATH') or os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'personal-db.sqlite')

def init_db():
    """初始化数据库连接和表结构"""
    db_dir = os.path.dirname(DB_PATH)
    Path(db_dir).mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode = WAL')
    
    # 创建表结构
    conn.executescript('''
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
    ''')
    
    conn.commit()
    print(f'✅ 数据库已初始化: {DB_PATH}')
    return conn

def get_dimension(conn, dimension_id):
    """获取单个维度"""
    cursor = conn.execute('SELECT * FROM personal_profiles WHERE dimension_id = ?', (dimension_id,))
    result = cursor.fetchone()
    if result:
        columns = ['dimension_id', 'dimension_name', 'value', 'value_type', 'updated_at', 'created_at']
        return dict(zip(columns, result))
    return None

def get_batch_dimensions(conn, dimension_ids):
    """批量获取维度"""
    placeholders = ','.join(['?'] * len(dimension_ids))
    query = f'SELECT * FROM personal_profiles WHERE dimension_id IN ({placeholders})'
    cursor = conn.execute(query, dimension_ids)
    columns = ['dimension_id', 'dimension_name', 'value', 'value_type', 'updated_at', 'created_at']
    results = cursor.fetchall()
    return [dict(zip(columns, row)) for row in results]

def set_dimension(conn, dimension_id, dimension_name, value, value_type='string'):
    """设置单个维度"""
    now = int(datetime.now().timestamp() * 1000)
    conn.execute('''
    INSERT INTO personal_profiles (dimension_id, dimension_name, value, value_type, updated_at, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(dimension_id) DO UPDATE SET
      dimension_name = excluded.dimension_name,
      value = excluded.value,
      value_type = excluded.value_type,
      updated_at = excluded.updated_at
    ''', (dimension_id, dimension_name, value, value_type, now, now))
    conn.commit()
    print(f'✅ 已设置维度: {dimension_id} = {value}')

def set_batch_dimensions(conn, data):
    """批量设置维度"""
    now = int(datetime.now().timestamp() * 1000)
    for dimension_id, value in data.items():
        dimension_name = dimension_id.split('.')[-1]
        conn.execute('''
        INSERT INTO personal_profiles (dimension_id, dimension_name, value, value_type, updated_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(dimension_id) DO UPDATE SET
          dimension_name = excluded.dimension_name,
          value = excluded.value,
          value_type = excluded.value_type,
          updated_at = excluded.updated_at
        ''', (dimension_id, dimension_name, value, 'string', now, now))
    conn.commit()
    print(f'✅ 已批量设置 {len(data)} 个维度')

def delete_dimension(conn, dimension_id):
    """删除维度"""
    cursor = conn.execute('DELETE FROM personal_profiles WHERE dimension_id = ?', (dimension_id,))
    conn.commit()
    if cursor.rowcount > 0:
        print(f'✅ 已删除维度: {dimension_id}')
    else:
        print(f'⚠️  维度不存在: {dimension_id}')

def list_all_dimensions(conn):
    """列出所有维度"""
    cursor = conn.execute('SELECT * FROM personal_profiles ORDER BY updated_at DESC')
    columns = ['dimension_id', 'dimension_name', 'value', 'value_type', 'updated_at', 'created_at']
    results = cursor.fetchall()
    print(f'\n📊 共有 {len(results)} 个维度:\n')
    for i, row in enumerate(results, 1):
        record = dict(zip(columns, row))
        print(f'{i}. {record["dimension_id"]}')
        print(f'   名称: {record["dimension_name"]}')
        print(f'   值: {record["value"]}')
        print(f'   更新时间: {datetime.fromtimestamp(record["updated_at"]/1000).strftime("%Y-%m-%d %H:%M:%S")}')
        print()

def export_json(conn):
    """导出为 JSON"""
    cursor = conn.execute('SELECT * FROM personal_profiles')
    columns = ['dimension_id', 'dimension_name', 'value', 'value_type', 'updated_at', 'created_at']
    results = cursor.fetchall()
    data = [dict(zip(columns, row)) for row in results]
    export_path = os.path.join(os.path.dirname(DB_PATH), 'personal-db-export.json')
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'✅ 已导出到: {export_path}')

def main():
    command = sys.argv[1] if len(sys.argv) > 1 else None
    args = sys.argv[2:]
    
    try:
        conn = init_db()
        
        if command == 'get':
            if not args:
                print('用法: python3 personal-db.py get <dimension_id>')
                sys.exit(1)
            result = get_dimension(conn, args[0])
            if result:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print('⚠️  维度不存在')
        
        elif command == 'get-batch':
            if not args:
                print('用法: python3 personal-db.py get-batch <dimension_id1,dimension_id2,...>')
                sys.exit(1)
            ids = args[0].split(',')
            results = get_batch_dimensions(conn, ids)
            print(json.dumps(results, ensure_ascii=False, indent=2))
        
        elif command == 'set':
            if len(args) < 3:
                print('用法: python3 personal-db.py set <dimension_id> <dimension_name> <value>')
                sys.exit(1)
            set_dimension(conn, args[0], args[1], args[2])
        
        elif command == 'set-batch':
            if not args:
                print('用法: python3 personal-db.py set-batch \'{\\"dim1\\": \\"value1\\", \\"dim2\\": \\"value2\\"}\'')
                sys.exit(1)
            data = json.loads(args[0])
            set_batch_dimensions(conn, data)
        
        elif command == 'delete':
            if not args:
                print('用法: python3 personal-db.py delete <dimension_id>')
                sys.exit(1)
            delete_dimension(conn, args[0])
        
        elif command == 'list':
            list_all_dimensions(conn)
        
        elif command == 'export':
            export_json(conn)
        
        else:
            print('''
HeyCube 个人档案管理工具

用法:
  python3 personal-db.py <command> [args]

命令:
  get <dimension_id>                    获取单个维度
  get-batch <dimension_id1,id2,...>     批量获取维度
  set <dimension_id> <name> <value>     设置单个维度
  set-batch '{"dim": "value"}'          批量设置维度
  delete <dimension_id>                 删除维度
  list                                  列出所有维度
  export                                导出为 JSON

示例:
  python3 personal-db.py get profile.career
  python3 personal-db.py get-batch "profile.career,behavior.work_habits"
  python3 personal-db.py set profile.career.career_stage "职业阶段" "资深"
  python3 personal-db.py set-batch '{"profile.career": "软件工程师", "behavior.work_habits.time_management": "番茄工作法"}'
  python3 personal-db.py list
  python3 personal-db.py export
            ''')
        
        conn.close()
    except Exception as e:
        print(f'❌ 错误: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
