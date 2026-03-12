#!/bin/bash
# OpenClaw Control Center 版本升级脚本

VERSION_FILE="package.json.backup"
CURRENT_VERSION=$(cat $VERSION_FILE | grep '"version"' | head -1 | awk -F'"' '{print $4}')

echo "当前版本: $CURRENT_VERSION"

# 读取版本号
MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
MINOR=$(echo $CURRENT_VERSION | cut -d. -f2)
PATCH=$(echo $CURRENT_VERSION | cut -d. -f3)

# 升级版本号
PATCH=$((PATCH + 1))
NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"

echo "新版本: $NEW_VERSION"

# 更新版本文件
cat > $VERSION_FILE << EOF
{
  "name": "openclaw-control-center",
  "version": "$NEW_VERSION",
  "description": "OpenClaw Control Center - Web UI 控制面板",
  "installDate": "2026-03-12",
  "status": "running",
  "config": {
    "gatewayUrl": "http://127.0.0.1:18789",
    "openclawHome": "/root/.openclaw",
    "uiHost": "0.0.0.0",
    "uiPort": 4310,
    "readonlyMode": true,
    "localTokenAuthRequired": true
  },
  "access": {
    "local": "http://127.0.0.1:4310",
    "external": "http://43.134.63.176:4310"
  },
  "changelog": [
    {
      "version": "$NEW_VERSION",
      "date": "$(date +%Y-%m-%d)",
      "changes": [
        "版本升级"
      ]
    }
  ]
}
EOF

echo "✅ 版本已升级到 $NEW_VERSION"
echo "请记录升级原因并提交到 Git"
