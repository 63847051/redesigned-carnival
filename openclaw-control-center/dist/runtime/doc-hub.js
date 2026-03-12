"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildStructuredDocHubFromSessions = buildStructuredDocHubFromSessions;
const node_crypto_1 = require("node:crypto");
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const session_conversations_1 = require("./session-conversations");
const MAX_DOC_TITLE_CHARS = 88;
const MAX_DOC_EXCERPT_CHARS = 240;
const MAX_DOC_CONTENT_CHARS = 4000;
const CACHE_TTL_MS = 45_000;
let cachedSnapshot;
let cacheAtMs = 0;
let cachePath = "";
async function buildStructuredDocHubFromSessions(input) {
    const now = new Date().toISOString();
    const indexPath = input.indexPath;
    const refreshFromSessions = input.refreshFromSessions ?? true;
    const nowMs = Date.now();
    if (cachedSnapshot &&
        cachePath === indexPath &&
        nowMs - cacheAtMs < CACHE_TTL_MS &&
        refreshFromSessions) {
        return cachedSnapshot;
    }
    const existing = await readStructuredDocStore(indexPath);
    if (!refreshFromSessions) {
        const result = {
            generatedAt: existing.generatedAt ?? now,
            sourcePath: indexPath,
            detail: existing.items.length > 0 ? `已读取历史入库 ${existing.items.length} 条。` : "尚无聊天结构化入库记录。",
            items: existing.items,
        };
        cachedSnapshot = result;
        cacheAtMs = nowMs;
        cachePath = indexPath;
        return result;
    }
    const maxSessions = clampInt(input.maxSessions, 8, 48, 24);
    const historyLimit = clampInt(input.historyLimit, 24, 240, 140);
    const maxDocsPerSession = clampInt(input.maxDocsPerSession, 1, 8, 3);
    const maxStoredDocs = clampInt(input.maxStoredDocs, 40, 800, 320);
    const candidates = [...input.snapshot.sessions]
        .sort((a, b) => toMs(b.lastMessageAt) - toMs(a.lastMessageAt) || a.sessionKey.localeCompare(b.sessionKey))
        .slice(0, maxSessions);
    const details = await Promise.all(candidates.map((session) => (0, session_conversations_1.getSessionConversationDetail)({
        snapshot: input.snapshot,
        client: input.client,
        sessionKey: session.sessionKey,
        historyLimit,
    })));
    const extracted = [];
    for (const detail of details) {
        if (!detail)
            continue;
        extracted.push(...extractStructuredDocsFromDetail(detail, maxDocsPerSession, now));
    }
    const mergedById = new Map(existing.items.map((item) => [item.id, item]));
    for (const item of extracted) {
        mergedById.set(item.id, item);
    }
    const merged = [...mergedById.values()]
        .sort((a, b) => toMs(b.sourceTimestamp) - toMs(a.sourceTimestamp) || toMs(b.updatedAt) - toMs(a.updatedAt))
        .slice(0, maxStoredDocs);
    const stored = {
        generatedAt: now,
        items: merged,
    };
    await writeStructuredDocStore(indexPath, stored);
    const snapshot = {
        generatedAt: now,
        sourcePath: indexPath,
        detail: `本轮扫描 ${candidates.length} 个会话，新增/刷新 ${extracted.length} 条，当前总计 ${merged.length} 条。`,
        items: merged,
    };
    cachedSnapshot = snapshot;
    cacheAtMs = nowMs;
    cachePath = indexPath;
    return snapshot;
}
function extractStructuredDocsFromDetail(detail, maxDocs, updatedAt) {
    const rows = [];
    const history = [...detail.history].reverse();
    for (const entry of history) {
        if (rows.length >= maxDocs)
            break;
        if (!isDocumentLikeMessage(entry))
            continue;
        const content = normalizeInlineText(entry.content);
        if (!content)
            continue;
        const title = inferDocTitle(content, detail.session.label ?? detail.session.sessionKey);
        const category = classifyDocCategory(title, content);
        const excerpt = toExcerpt(content, MAX_DOC_EXCERPT_CHARS);
        const sourceTimestamp = normalizeIso(entry.timestamp) ??
            normalizeIso(detail.latestHistoryAt) ??
            normalizeIso(detail.session.lastMessageAt) ??
            updatedAt;
        const id = createDocId(detail.session.sessionKey, sourceTimestamp, title, excerpt);
        rows.push({
            id,
            title,
            excerpt,
            content: safeTruncate(content, MAX_DOC_CONTENT_CHARS),
            category,
            sourceSessionKey: detail.session.sessionKey,
            sourceAgentId: detail.session.agentId ?? undefined,
            sourceTimestamp,
            updatedAt,
        });
    }
    return rows;
}
function isDocumentLikeMessage(item) {
    if (item.kind !== "message")
        return false;
    const role = item.role.toLowerCase();
    if (!["assistant", "system", "model", "unknown"].includes(role))
        return false;
    const content = item.content.trim();
    if (content.length < 80)
        return false;
    if (/^#{1,4}\s+/m.test(content))
        return true;
    if (/```[\s\S]{12,}```/m.test(content))
        return true;
    if (/\n\d+\.\s+/.test(content) && /\n[-*]\s+/.test(content))
        return true;
    if (/\n[-*]\s+/.test(content) && content.length >= 320)
        return true;
    if (/\b(prd|runbook|architecture|roadmap|spec|design doc|postmortem|brief)\b/i.test(content))
        return true;
    if (/(计划|方案|总结|日报|周报|复盘|提案|执行步骤|行动项|架构|需求)/.test(content))
        return true;
    return false;
}
function inferDocTitle(content, fallback) {
    const heading = content
        .split(/\r?\n/)
        .map((line) => line.trim())
        .find((line) => /^#{1,4}\s+/.test(line))
        ?.replace(/^#{1,4}\s+/, "")
        .trim() ?? "";
    if (heading)
        return safeTruncate(heading, MAX_DOC_TITLE_CHARS);
    const firstLine = content
        .split(/\r?\n/)
        .map((line) => line.trim())
        .find((line) => line.length > 8) ?? fallback;
    return safeTruncate(firstLine.replace(/^[-*]\s+/, ""), MAX_DOC_TITLE_CHARS);
}
function classifyDocCategory(title, content) {
    const raw = `${title}\n${content}`.toLowerCase();
    if (/(日报|周报|总结|复盘|weekly|daily|retrospective)/.test(raw))
        return "总结复盘";
    if (/(计划|路线图|roadmap|milestone|next step)/.test(raw))
        return "计划路线";
    if (/(spec|prd|需求|设计|架构|architecture|api)/.test(raw))
        return "规格设计";
    if (/(runbook|sop|流程|操作手册|故障)/.test(raw))
        return "操作手册";
    if (/(newsletter|草稿|draft|公告|文案)/.test(raw))
        return "内容草稿";
    return "会话文档";
}
function createDocId(sessionKey, timestamp, title, excerpt) {
    const hash = (0, node_crypto_1.createHash)("sha1")
        .update(`${sessionKey}|${timestamp}|${title}|${excerpt}`)
        .digest("hex");
    return `chatdoc-${hash.slice(0, 24)}`;
}
async function readStructuredDocStore(indexPath) {
    try {
        const raw = await (0, promises_1.readFile)(indexPath, "utf8");
        const parsed = JSON.parse(raw);
        const generatedAt = typeof parsed.generatedAt === "string" && parsed.generatedAt.trim()
            ? parsed.generatedAt
            : new Date().toISOString();
        const rawItems = Array.isArray(parsed.items) ? parsed.items : [];
        const items = [];
        for (const row of rawItems) {
            if (!row || typeof row !== "object")
                continue;
            const item = row;
            const sourceSessionKey = asString(item.sourceSessionKey);
            const title = asString(item.title);
            const excerpt = asString(item.excerpt);
            const category = asString(item.category);
            const sourceTimestamp = normalizeIso(asString(item.sourceTimestamp)) ?? new Date().toISOString();
            const updatedAt = normalizeIso(asString(item.updatedAt)) ?? sourceTimestamp;
            if (!sourceSessionKey || !title || !excerpt || !category)
                continue;
            const id = asString(item.id) ?? createDocId(sourceSessionKey, sourceTimestamp, title, excerpt);
            items.push({
                id,
                title: safeTruncate(title, MAX_DOC_TITLE_CHARS),
                excerpt: safeTruncate(excerpt, MAX_DOC_EXCERPT_CHARS),
                content: safeTruncate(asString(item.content) ?? excerpt, MAX_DOC_CONTENT_CHARS),
                category: safeTruncate(category, 24),
                sourceSessionKey,
                sourceAgentId: asString(item.sourceAgentId),
                sourceTimestamp,
                updatedAt,
            });
        }
        return { generatedAt, items };
    }
    catch {
        return {
            generatedAt: new Date().toISOString(),
            items: [],
        };
    }
}
async function writeStructuredDocStore(indexPath, store) {
    await (0, promises_1.mkdir)((0, node_path_1.dirname)(indexPath), { recursive: true });
    await (0, promises_1.writeFile)(indexPath, `${JSON.stringify(store, null, 2)}\n`, "utf8");
}
function toExcerpt(input, maxLength) {
    const normalized = normalizeInlineText(input);
    return safeTruncate(normalized, maxLength);
}
function normalizeInlineText(input) {
    return input.replace(/\r/g, "\n").replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();
}
function safeTruncate(input, maxLength) {
    if (input.length <= maxLength)
        return input;
    if (maxLength <= 3)
        return input.slice(0, Math.max(0, maxLength));
    return `${input.slice(0, maxLength - 3)}...`;
}
function normalizeIso(input) {
    if (!input)
        return undefined;
    const ms = Date.parse(input);
    if (!Number.isFinite(ms))
        return undefined;
    return new Date(ms).toISOString();
}
function clampInt(value, min, max, fallback) {
    if (!Number.isFinite(value))
        return fallback;
    const normalized = Math.trunc(value);
    if (normalized < min)
        return min;
    if (normalized > max)
        return max;
    return normalized;
}
function toMs(value) {
    if (!value)
        return 0;
    const ms = Date.parse(value);
    return Number.isFinite(ms) ? ms : 0;
}
function asString(value) {
    if (typeof value !== "string")
        return undefined;
    const trimmed = value.trim();
    return trimmed ? trimmed : undefined;
}
