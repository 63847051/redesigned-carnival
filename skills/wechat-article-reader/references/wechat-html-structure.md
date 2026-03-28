# WeChat Article HTML Structure Reference

This document describes the HTML structure of WeChat Official Account articles for parsing purposes.

## Basic Structure

```html
<!DOCTYPE html>
<html>
<head>
  <meta property="og:title" content="文章标题">
  <meta property="og:description" content="文章摘要">
  <meta property="og:article:author" content="作者名称">
</head>
<body>
  <div class="rich_media_area">
    <div class="rich_media_title">文章标题</div>
    <div class="rich_media_meta_list">
      <em class="rich_media_meta_text">发布时间</em>
    </div>
    <div id="js_content" class="rich_media_content">
      <!-- 主要内容 -->
    </div>
  </div>
</body>
</html>
```

## Key Elements

### Title

```html
<!-- Method 1: meta tag -->
<meta property="og:title" content="文章标题">

<!-- Method 2: rich_media_title -->
<div class="rich_media_title">文章标题</div>
```

### Author

```html
<meta property="og:article:author" content="作者名称">
```

### Publish Time

```html
<em class="rich_media_meta_text">2024-03-15</em>
```

### Main Content

```html
<div id="js_content" class="rich_media_content">
  <p>段落内容</p>
  <section>...</section>
  <img src="image_url">
</div>
```

## Common Patterns

### Images

```html
<img
  data-type="png"
  data-src="https://mmbiz.qpic.cn/..."
  class="rich_pages wxw-img"
>
```

### Videos

```html
<mpvideo
  class="wxw-player__video"
  poster="https://..."
  src="https://..."
>
</mpvideo>
```

### Links

```html
<a href="external_url">链接文字</a>
```

## Anti-Bot Detection

WeChat uses several anti-bot mechanisms:

1. **User-Agent detection** - Blocks non-browser UAs
2. **Cookie validation** - Requires session cookies
3. **JS rendering** - Content loaded via JavaScript
4. **Lazy loading** - Images loaded on scroll

## Bypass Strategies

### 1. iPhone User-Agent

```
Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.15(0x18000f2f) NetType/WIFI Language/zh_CN
```

### 2. Cookie Reuse

Reuse valid session cookies:
```
cookies = {
    'key': 'value',
    'pass_ticket': '...',
    'wxtokenkey': '...'
}
```

### 3. Selenium Automation

Full browser rendering to bypass all checks.

## Content Cleaning

Remove these artifacts:

```html
<!-- Common footers to remove -->
本文转载自...
长按识别二维码关注
点击阅读原文
```

## CSS Selectors

```css
/* Title */
.rich_media_title
meta[property='og:title']

/* Content */
#js_content
.rich_media_content

/* Author */
meta[property='og:article:author']

/* Publish Time */
.rich_media_meta_text
```

## Testing

Test URL structure:
- Valid: `https://mp.weixin.qq.com/s/XXXXX`
- Valid: `https://mp.weixin.qq.com/s?__biz=...&mid=...&sn=...`
- Invalid: `https://weixin.qq.com/...` (not article)
- Invalid: `https://mp.weixin.qq.com/cgi-bin/...` (API)
