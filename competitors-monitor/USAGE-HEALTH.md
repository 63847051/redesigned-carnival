# 健康管理助手 - 使用指南

## 概述

健康管理助手监控日常健康指标（心率、血压、睡眠、步数、饮水量），提供健康建议和异常预警。

## 功能特性

- **日常指标监控**: 心率、血压、睡眠、步数、饮水量
- **异常告警**: 识别心率异常、血压偏高、睡眠不足等活动量问题
- **健康建议**: 基于指标提供个性化健康建议
- **趋势追踪**: 对比历史数据发现健康变化

## 配置说明

编辑 `config/health.json`:

```json
{
  "data_sources": {
    "manual_input": {
      "enabled": true,
      "last_values": {
        "weight": 70,
        "heart_rate": 72,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "sleep_hours": 7.5,
        "steps": 8000,
        "water_intake": 2000
      }
    }
  },
  "check_rules": {
    "heart_rate_abnormal_low": 50,
    "heart_rate_abnormal_high": 100,
    "blood_pressure_systolic_high": 140,
    "sleep_minimum_hours": 6,
    "steps_minimum": 5000,
    "water_minimum_ml": 1500
  },
  "goals": {
    "weight_target": 68,
    "sleep_target": 8,
    "steps_target": 10000,
    "water_target": 2500
  }
}
```

## 运行方式

```bash
cd /root/.openclaw/workspace/competitors-monitor
python3 plugins/health.py
```

## 输出示例

```
获取到 1 条健康数据
发现 2 条健康提醒
  [INFO] 睡眠不足: 5.5 小时 (建议: 6+ 小时)
  [INFO] 活动量不足: 3000 步 (建议: 5000+ 步)

## 📊 今日健康摘要

### 身体指标

- 心率: 72 bpm
- 血压: 120/80 mmHg
- 睡眠: 5.5 小时
- 步数: 3000 步
- 饮水: 2000 ml

### ⚠️ 健康提醒

🟡 睡眠不足: 5.5 小时 (建议: 6+ 小时)
🟡 活动量不足: 3000 步 (建议: 5000+ 步)
```

## 告警类型

| 类型 | 严重程度 | 说明 |
|------|----------|------|
| abnormal_heart_rate | warning | 心率异常（过高或过低） |
| high_blood_pressure | warning | 血压偏高 |
| poor_sleep | info | 睡眠不足 |
| low_activity | info | 活动量不足 |
| low_water | info | 饮水量不足 |

## 手动更新数据

修改 `config/health.json` 中的 `last_values` 部分更新您的最新健康数据。

## 集成健康设备（高级）

### Apple Health

1. 使用 "Apple Health Export" 等工具导出健康数据
2. 在配置中设置 `export_path`

### Google Fit

1. 在 Google Cloud Console 创建项目
2. 启用 Fit API
3. 下载凭证 JSON 文件
4. 在配置中设置 `credentials_file`

## 定时运行

可以使用 crontab 定时运行:

```bash
# 每天早上 8 点运行
0 8 * * * cd /root/.openclaw/workspace/competitors-monitor && python3 plugins/health.py >> /var/log/health.log 2>&1
```
