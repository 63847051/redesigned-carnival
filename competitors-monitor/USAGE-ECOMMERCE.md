# 电商价格监控 - 使用指南

## 概述

电商价格监控帮助跟踪多个电商平台（京东、天猫、淘宝、拼多多）的商品价格变化，及时发现降价促销信息。

## 功能特性

- **多平台监控**: 支持京东、天猫、淘宝、拼多多
- **价格变化检测**: 自动识别降价/涨价
- **阈值告警**: 自定义价格变化百分比触发告警
- **库存监控**: 监控商品缺货状态

## 配置说明

编辑 `config/ecommerce-price.json`:

```json
{
  "targets": [
    {
      "name": "iPhone 15 Pro",
      "jd_sku": "100086924",
      "taobao_item_id": "123456789",
      "pdd_goods_id": "abcdef",
      "price_threshold": 100,
      "alert_on_price_drop": true
    }
  ],
  "check_rules": {
    "price_change_threshold": 0.05,
    "alert_on_out_of_stock": true
  }
}
```

## 运行方式

```bash
cd /root/.openclaw/workspace/competitors-monitor
python3 plugins/ecommerce.py
```

## 输出示例

```
获取到 6 条价格数据
发现 0 条价格变化

## 📊 电商价格监控报告

### iPhone 15 Pro

- jd: ¥7999 ✅
- taobao: ¥7899 ✅
- pdd: ¥7699 ✅

### MacBook Air M3

- jd: ¥9499 ✅
- taobao: ¥9299 ✅
- pdd: ¥8999 ✅
```

## 数据源配置

### 京东 API

1. 访问京东联盟开放平台
2. 创建应用获取 App Key 和 App Secret
3. 配置:

```json
"jd": {
  "enabled": true,
  "api_key": "YOUR_JD_API_KEY"
}
```

### 淘宝/天猫 API

1. 访问淘宝开放平台
2. 创建应用获取 App Key 和 App Secret
3. 配置:

```json
"taobao": {
  "enabled": true,
  "app_key": "YOUR_APP_KEY",
  "app_secret": "YOUR_APP_SECRET"
}
```

### 网页抓取

默认使用模拟数据进行演示。启用真实网页抓取需配置代理:

```json
"web_scraping": {
  "enabled": true,
  "use_proxy": true,
  "proxy_url": "http://your-proxy:port"
}
```

## 告警类型

| 类型 | 严重程度 | 说明 |
|------|----------|------|
| price_drop | info | 价格下降 |
| price_increase | warning | 价格上升 |
| out_of_stock | warning | 商品售罄 |

## 价格变化检测

系统会自动保存上次价格并与当前价格对比:

- 降价超过阈值 (默认 5%): 触发降价告警
- 涨价超过阈值: 触发涨价告警
- 库存状态变化: 触发缺货告警
