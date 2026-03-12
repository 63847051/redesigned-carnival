# 飞书工作日志配置

## 表格连接信息

- **表格名称**: 蓝色光标上海办公室工作日志
- **Wiki 链接**: https://ux7aumj3ud.feishu.cn/wiki/KSlQwODcAidSqVkuiLzcOLlrnug?table=tbl5s8TEZ0tKhEm7&view=vewUneokIL
- **app_token**: BISAbNgYXa7Do1sc36YcBChInnS
- **table_id**: tbl5s8TEZ0tKhEm7

## 字段映射

### 字段 ID 列表

- `fldbZ2CWW1` - 内容 (Text, Primary)
- `fldXK7KcJT` - 创建日期 (DateTime)
- `flduvO2SLV` - 完成时间 (DateTime)
- `fld45frLAf` - 备注 (Text)
- `fld8CvBIBc` - 附件 (Attachment)
- `fldpJtUjnR` - 项目状态 (SingleSelect)
- `fldEF5uhQx` - 项目类型 (SingleSelect)
- `flds8zn1ct` - 优先级别 (SingleSelect)

### 选项值

**项目状态 (fldpJtUjnR)**:
- `optS8Oh6TA` - 待确认
- `opt1z5rN5Z` - 待完成
- `optGu1hRZO` - 已完成

**项目类型 (fldEF5uhQx)**:
- `optiz59yU0` - 现场
- `optjy8DB4t` - 设计
- `opt3evVcle` - 施工
- `optTA5aXL9` - 机电

**优先级别 (flds8zn1ct)**:
- `optevFOsPs` - 第一优先
- `optpI04mBd` - 重要
- `optn0dMrKg` - 普通重要

## 日期处理

- **格式**: yyyy/MM/dd
- **时间戳**: 毫秒级 Unix 时间戳
- **示例**: 2026-03-03 → `Date.parse("2026-03-03")` → `1709449200000`

## 工具使用模板

### 获取所有记录

```bash
feishu_bitable_list_records \
  --app_token "BISAbNgYXa7Do1sc36YcBChInnS" \
  --table_id "tbl5s8TEZ0tKhEm7" \
  --page_size 100
```

### 创建记录

```json
{
  "fields": {
    "内容": "工作内容描述",
    "创建日期": 1709449200000,
    "项目状态": "待完成",
    "项目类型": "现场",
    "优先级别": "普通重要"
  }
}
```

### 更新记录

```json
{
  "fields": {
    "项目状态": "已完成",
    "完成时间": 1709535600000,
    "备注": "补充说明"
  }
}
```
