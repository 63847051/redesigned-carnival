# Installation Guide

WeChat Article Reader - Installation Instructions

## Method 1: Via SkillHub (Recommended)

```bash
skillhub install wechat-article-reader
```

This will automatically install the skill to your OpenClaw workspace.

## Method 2: Manual Installation

### Step 1: Clone or Download

```bash
# Git clone
git clone https://github.com/your-repo/wechat-article-reader.git

# Or download and extract
wget https://github.com/your-repo/wechat-article-reader/archive/main.zip
unzip main.zip
```

### Step 2: Install Dependencies

```bash
cd wechat-article-reader

# Basic dependencies (required)
pip install requests beautifulsoup4

# Optional (for screenshots)
pip install selenium
```

### Step 3: Verify Installation

```bash
python -c "import requests; import bs4; print('✅ Dependencies installed')"
```

### Step 4: Test

```bash
python scripts/read-wechat.py https://mp.weixin.qq.com/s/test-article
```

## System Requirements

- **Python**: 3.6 or higher
- **OS**: Linux, macOS, Windows
- **Memory**: 512MB minimum (1GB recommended)
- **Network**: Stable internet connection

## Optional: Chrome/Chromium (for screenshots)

If you want to capture screenshots:

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y chromium-browser
```

### macOS

```bash
brew install --cask chromium
```

### Windows

Download from: https://www.chromium.org/

## Troubleshooting

### Issue: Module not found

```bash
# Error: ModuleNotFoundError: No module named 'requests'
# Solution:
pip install requests beautifulsoup4
```

### Issue: Selenium errors

```bash
# Error: WebDriverException
# Solution: Install Chrome/Chromium
# Or disable screenshot feature
```

### Issue: Permission denied

```bash
# Error: Permission denied when saving files
# Solution:
chmod +x scripts/read-wechat.py
```

## Uninstallation

```bash
# Via SkillHub
skillhub uninstall wechat-article-reader

# Manual
rm -rf wechat-article-reader
```

## Next Steps

- Read [SKILL.md](SKILL.md) for detailed usage
- Check [README.md](README.md) for quick start
- Run tests: `python tests/test_wechat_reader.py`

---

**Need help?** Open an issue on GitHub or check the documentation.
