"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadLatestDigest = loadLatestDigest;
exports.renderLatestDigestPage = renderLatestDigestPage;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const DIGEST_DIR = (0, node_path_1.join)(process.cwd(), "runtime", "digests");
async function loadLatestDigest() {
    const generatedAt = new Date().toISOString();
    try {
        const files = await (0, promises_1.readdir)(DIGEST_DIR);
        const latest = files
            .filter((name) => name.endsWith(".md"))
            .sort((a, b) => b.localeCompare(a))[0];
        if (!latest) {
            return { generatedAt };
        }
        const path = (0, node_path_1.join)(DIGEST_DIR, latest);
        const markdown = await (0, promises_1.readFile)(path, "utf8");
        return {
            generatedAt,
            date: latest.slice(0, -3),
            path,
            markdown,
            html: renderMarkdownDigest(markdown),
        };
    }
    catch {
        return { generatedAt };
    }
}
function renderLatestDigestPage(digest) {
    if (!digest.markdown || !digest.html) {
        return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Digest Latest</title>
  <style>
    body { font-family: "SF Mono", Menlo, monospace; background: #0b1016; color: #d6e7f9; margin: 0; padding: 16px; }
    .meta { color: #93aac2; font-size: 12px; }
    a { color: #7dd3fc; }
    .card { margin-top: 10px; border: 1px solid #27405a; border-radius: 8px; padding: 12px; background: #111923; }
  </style>
</head>
<body>
  <h1>Latest Digest</h1>
  <div class="meta">generatedAt=${escapeHtml(digest.generatedAt)} | status=missing</div>
  <div class="card">No digest markdown found in <code>${escapeHtml(DIGEST_DIR)}</code>.</div>
  <p class="meta"><a href="/">home</a></p>
</body>
</html>`;
    }
    return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Digest ${escapeHtml(digest.date ?? "latest")}</title>
  <style>
    body { font-family: "SF Mono", Menlo, monospace; background: #0b1016; color: #d6e7f9; margin: 0; padding: 16px; }
    .meta { color: #93aac2; font-size: 12px; }
    a { color: #7dd3fc; }
    .card { margin-top: 10px; border: 1px solid #27405a; border-radius: 8px; padding: 12px; background: #111923; }
    h1,h2,h3 { margin: 0; }
    h2,h3 { margin-top: 14px; }
    p { margin: 8px 0; }
    ul { margin: 8px 0 8px 18px; padding: 0; }
    code { color: #9bd5ff; }
  </style>
</head>
<body>
  <h1>Latest Digest</h1>
  <div class="meta">date=${escapeHtml(digest.date ?? "unknown")} | generatedAt=${escapeHtml(digest.generatedAt)}</div>
  <div class="meta">source=${escapeHtml(digest.path ?? "n/a")}</div>
  <div class="card">${digest.html}</div>
  <p class="meta"><a href="/">home</a></p>
</body>
</html>`;
}
function renderMarkdownDigest(markdown) {
    const lines = markdown.replace(/\r/g, "").split("\n");
    const out = [];
    let inList = false;
    const closeList = () => {
        if (inList) {
            out.push("</ul>");
            inList = false;
        }
    };
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) {
            closeList();
            continue;
        }
        if (trimmed.startsWith("### ")) {
            closeList();
            out.push(`<h3>${renderInline(trimmed.slice(4))}</h3>`);
            continue;
        }
        if (trimmed.startsWith("## ")) {
            closeList();
            out.push(`<h2>${renderInline(trimmed.slice(3))}</h2>`);
            continue;
        }
        if (trimmed.startsWith("# ")) {
            closeList();
            out.push(`<h1>${renderInline(trimmed.slice(2))}</h1>`);
            continue;
        }
        if (trimmed.startsWith("- ")) {
            if (!inList) {
                out.push("<ul>");
                inList = true;
            }
            out.push(`<li>${renderInline(trimmed.slice(2))}</li>`);
            continue;
        }
        closeList();
        out.push(`<p>${renderInline(trimmed)}</p>`);
    }
    closeList();
    return out.join("\n");
}
function renderInline(input) {
    const escaped = escapeHtml(input);
    return escaped.replace(/`([^`]+)`/g, (_match, group) => `<code>${group}</code>`);
}
function escapeHtml(input) {
    return input
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}
