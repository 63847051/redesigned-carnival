"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.listSessionConversations = listSessionConversations;
exports.getSessionConversationDetail = getSessionConversationDetail;
exports.inferSessionExecutionChainFromSessionKey = inferSessionExecutionChainFromSessionKey;
const HISTORY_ARRAY_KEYS = ["history", "messages", "items", "entries", "events", "conversation"];
const ROLE_KEYS = ["role", "speaker", "source"];
const ROLE_TYPE_KEYS = ["type"];
const AUTHOR_KEYS = ["author", "agent", "agentId", "name", "from"];
const TIME_KEYS = ["timestamp", "time", "createdAt", "updatedAt", "at", "ts"];
const TOOL_NAME_KEYS = [
    "toolName",
    "tool",
    "toolId",
    "tool_id",
    "function",
    "functionName",
    "toolCall",
    "tool_call",
    "action",
];
const TOOL_STATUS_KEYS = ["status", "state", "outcome", "resultStatus"];
const TOOL_INPUT_KEYS = ["arguments", "args", "input", "params", "command", "query", "payload"];
const TOOL_OUTPUT_KEYS = ["result", "output", "response", "return", "observation", "error"];
const TOOL_HINT_KEYS = [
    "tool",
    "toolName",
    "tool_call",
    "toolCall",
    "function",
    "arguments",
    "args",
    "result",
    "output",
];
const EXECUTION_EVENT_KEYS = [
    "event",
    "kind",
    "action",
    "type",
    "operation",
    "eventType",
    "name",
    "status",
];
const PARENT_SESSION_KEYS = [
    "parentSessionKey",
    "parent_session_key",
    "parentSession",
    "parent_session",
    "sourceSessionKey",
    "source_session_key",
];
const CHILD_SESSION_KEYS = [
    "childSessionKey",
    "child_session_key",
    "spawnedSessionKey",
    "spawned_session_key",
    "targetSessionKey",
    "target_session_key",
    "sessionKey",
    "session_key",
];
const SESSION_KEY_REGEX = /agent:[A-Za-z0-9_.-]+(?::[A-Za-z0-9_.-]+)+/g;
const MAX_ENTRY_CONTENT_CHARS = 1200;
const MAX_SNIPPET_CHARS = 220;
const MAX_TOOL_SEGMENT_CHARS = 280;
const KNOWN_ROLE_TYPES = new Set(["user", "assistant", "system", "tool"]);
async function listSessionConversations(input) {
    const page = normalizePage(input.page);
    const pageSize = normalizePageSize(input.pageSize);
    const historyLimit = normalizeHistoryLimit(input.historyLimit);
    const sessions = input.snapshot.sessions
        .filter((session) => matchesSession(session, input.filters))
        .sort(compareSessions);
    const total = sessions.length;
    const start = (page - 1) * pageSize;
    const paged = sessions.slice(start, start + pageSize);
    const items = await Promise.all(paged.map(async (session) => {
        const history = await readSessionHistory(input.client, session.sessionKey, historyLimit);
        const latest = pickLatestMessage(history.messages);
        return {
            ...session,
            latestSnippet: latest ? summarizeSnippet(latest.content) : undefined,
            latestRole: latest?.role,
            latestKind: latest?.kind,
            latestToolName: latest?.toolName,
            latestHistoryAt: latest?.timestamp,
            historyCount: history.messages.length,
            toolEventCount: history.messages.filter((message) => message.kind === "tool_event").length,
            historyError: history.error,
            executionChain: inferSessionExecutionChain(session, history.messages),
        };
    }));
    return {
        generatedAt: new Date().toISOString(),
        total,
        page,
        pageSize,
        filters: input.filters,
        items,
    };
}
async function getSessionConversationDetail(input) {
    const sessionKey = input.sessionKey.trim();
    if (!sessionKey)
        return null;
    const session = input.snapshot.sessions.find((item) => item.sessionKey === sessionKey);
    if (!session)
        return null;
    const historyLimit = normalizeHistoryLimit(input.historyLimit, 50);
    const history = await readSessionHistory(input.client, sessionKey, historyLimit);
    const latest = pickLatestMessage(history.messages);
    const status = input.snapshot.statuses.find((item) => item.sessionKey === sessionKey);
    return {
        generatedAt: new Date().toISOString(),
        session,
        status,
        latestSnippet: latest ? summarizeSnippet(latest.content) : undefined,
        latestRole: latest?.role,
        latestKind: latest?.kind,
        latestToolName: latest?.toolName,
        latestHistoryAt: latest?.timestamp,
        historyCount: history.messages.length,
        history: history.messages,
        historyError: history.error,
        executionChain: inferSessionExecutionChain(session, history.messages),
    };
}
function inferSessionExecutionChainFromSessionKey(session) {
    return inferSessionExecutionChain(session, []);
}
async function readSessionHistory(client, sessionKey, limit) {
    try {
        const response = await client.sessionsHistory({ sessionKey, limit });
        return {
            messages: normalizeHistoryMessages(response, limit),
        };
    }
    catch (error) {
        return {
            messages: [],
            error: error instanceof Error ? error.message : "Failed to read session history.",
        };
    }
}
function normalizeHistoryMessages(response, limit) {
    const fromJson = response.json ? normalizeHistoryFromJson(response.json) : [];
    const normalized = fromJson.length > 0 ? fromJson : normalizeHistoryFromText(response.rawText);
    if (normalized.length <= limit)
        return normalized;
    return normalized.slice(-limit);
}
function normalizeHistoryFromJson(input) {
    const entries = extractHistoryArray(input);
    if (entries.length === 0)
        return [];
    const messages = [];
    for (const entry of entries) {
        const parsed = parseHistoryEntry(entry);
        if (!parsed)
            continue;
        messages.push(parsed);
    }
    return messages;
}
function extractHistoryArray(input) {
    if (Array.isArray(input))
        return input;
    const obj = asObject(input);
    if (!obj)
        return [];
    for (const key of HISTORY_ARRAY_KEYS) {
        const value = obj[key];
        if (Array.isArray(value))
            return value;
    }
    for (const key of ["data", "result", "payload"]) {
        const nested = obj[key];
        const nestedObj = asObject(nested);
        if (!nestedObj)
            continue;
        for (const historyKey of HISTORY_ARRAY_KEYS) {
            const value = nestedObj[historyKey];
            if (Array.isArray(value))
                return value;
        }
    }
    return [];
}
function parseHistoryEntry(input) {
    if (typeof input === "string") {
        const content = normalizeSpace(input);
        if (!content)
            return null;
        const executionEvent = parseExecutionEventFromText(content);
        if (executionEvent)
            return executionEvent;
        return buildMessageEntry({
            kind: "message",
            role: "unknown",
            content,
        });
    }
    const obj = asObject(input);
    if (!obj)
        return null;
    const messageObj = asObject(obj.message);
    const executionEvent = parseExecutionEvent(obj);
    if (executionEvent) {
        return executionEvent;
    }
    if (looksLikeToolEvent(obj)) {
        return parseToolEvent(obj);
    }
    const role = extractRole(obj, messageObj) ?? "unknown";
    const author = extractAuthor(obj, messageObj);
    const timestamp = extractTimestamp(obj, messageObj);
    const content = extractEntryContent(obj, messageObj);
    if (!content)
        return null;
    return buildMessageEntry({
        kind: "message",
        role,
        author,
        content,
        timestamp,
    });
}
function parseToolEvent(obj) {
    const toolName = inferToolName(obj) ?? "tool";
    const toolStatus = firstString(obj, TOOL_STATUS_KEYS);
    const messageObj = asObject(obj.message);
    const role = extractRole(obj, messageObj) ?? "tool";
    const author = extractAuthor(obj, messageObj);
    const timestamp = extractTimestamp(obj, messageObj);
    const inputPreview = firstPreview(obj, TOOL_INPUT_KEYS, MAX_TOOL_SEGMENT_CHARS);
    const outputPreview = firstPreview(obj, TOOL_OUTPUT_KEYS, MAX_TOOL_SEGMENT_CHARS);
    const fallbackContent = extractEntryContent(obj, messageObj);
    const parts = [];
    if (inputPreview)
        parts.push(`in=${inputPreview}`);
    if (outputPreview)
        parts.push(`out=${outputPreview}`);
    const content = parts.length > 0 ? parts.join(" | ") : fallbackContent;
    if (!content)
        return null;
    return buildMessageEntry({
        kind: "tool_event",
        role,
        author,
        content,
        timestamp,
        toolName,
        toolStatus,
    });
}
function parseExecutionEvent(obj) {
    const eventKind = inferExecutionEventKind(obj);
    if (!eventKind)
        return null;
    const messageObj = asObject(obj.message);
    const role = extractRole(obj, messageObj) ?? "system";
    const author = extractAuthor(obj, messageObj);
    const timestamp = extractTimestamp(obj, messageObj);
    const toolName = inferToolName(obj);
    const toolStatus = firstString(obj, TOOL_STATUS_KEYS);
    const content = extractEntryContent(obj, messageObj) || `${eventKind} event`;
    const refs = extractExecutionSessionRefs(obj, content);
    return buildMessageEntry({
        kind: eventKind,
        role,
        author,
        content,
        timestamp,
        toolName,
        toolStatus,
        parentSessionKey: refs.parentSessionKey,
        childSessionKey: refs.childSessionKey,
    });
}
function parseExecutionEventFromText(content) {
    const kind = inferExecutionEventKindFromText(content);
    if (!kind)
        return null;
    const refs = extractExecutionSessionRefs({}, content);
    return buildMessageEntry({
        kind,
        role: "system",
        content,
        parentSessionKey: refs.parentSessionKey,
        childSessionKey: refs.childSessionKey,
        inferred: true,
    });
}
function buildMessageEntry(input) {
    const truncatedContent = truncateText(input.content, MAX_ENTRY_CONTENT_CHARS);
    return {
        kind: input.kind,
        role: input.role,
        author: input.author,
        content: truncatedContent.text,
        timestamp: input.timestamp,
        toolName: input.toolName,
        toolStatus: input.toolStatus,
        truncated: truncatedContent.truncated || undefined,
        parentSessionKey: input.parentSessionKey,
        childSessionKey: input.childSessionKey,
        inferred: input.inferred || undefined,
    };
}
function looksLikeToolEvent(obj) {
    const roleValue = (extractRole(obj, asObject(obj.message)) ?? "").toLowerCase();
    if (roleValue.includes("tool"))
        return true;
    const typeValue = (asString(obj.type) ?? "").toLowerCase();
    if (typeValue.includes("tool"))
        return true;
    const hasHint = TOOL_HINT_KEYS.some((key) => key in obj);
    if (!hasHint)
        return false;
    const hasName = Boolean(inferToolName(obj));
    if (hasName)
        return true;
    return TOOL_OUTPUT_KEYS.some((key) => key in obj) && TOOL_INPUT_KEYS.some((key) => key in obj);
}
function inferToolName(obj) {
    const direct = firstString(obj, TOOL_NAME_KEYS);
    if (direct)
        return direct;
    const toolObj = asObject(obj.tool);
    if (toolObj) {
        const nested = firstString(toolObj, ["name", "toolName", "id", "key"]);
        if (nested)
            return nested;
    }
    const functionObj = asObject(obj.function);
    if (functionObj) {
        const nested = firstString(functionObj, ["name", "toolName"]);
        if (nested)
            return nested;
    }
    const callObj = asObject(obj.tool_call) ?? asObject(obj.toolCall);
    if (callObj) {
        const nested = firstString(callObj, ["name", "toolName", "id"]);
        if (nested)
            return nested;
    }
    return undefined;
}
function inferExecutionEventKind(obj) {
    const messageObj = asObject(obj.message);
    const signals = [
        ...EXECUTION_EVENT_KEYS.map((key) => firstString(obj, [key])),
        inferToolName(obj),
        extractEntryContent(obj, messageObj),
    ]
        .filter((item) => typeof item === "string" && item.trim().length > 0)
        .map((item) => item.toLowerCase());
    for (const signal of signals) {
        const eventKind = inferExecutionEventKindFromText(signal);
        if (eventKind)
            return eventKind;
    }
    return undefined;
}
function inferExecutionEventKindFromText(input) {
    const lower = input.toLowerCase();
    if (/\bsessions?_spawn\b/.test(lower) || /\bspawn(?:ed|ing)?\b/.test(lower))
        return "spawn";
    if (/\baccepted\b/.test(lower) || /\baccept(?:ed|ing)?\b/.test(lower))
        return "accepted";
    return undefined;
}
function extractExecutionSessionRefs(obj, content) {
    const parentSessionKey = firstString(obj, [...PARENT_SESSION_KEYS]);
    const childSessionKey = firstString(obj, [...CHILD_SESSION_KEYS]);
    if (parentSessionKey && childSessionKey) {
        return { parentSessionKey, childSessionKey };
    }
    const contentKeys = extractSessionKeys(content);
    if (contentKeys.length >= 2) {
        return {
            parentSessionKey: parentSessionKey ?? contentKeys[0],
            childSessionKey: childSessionKey ?? contentKeys[1],
        };
    }
    return {
        parentSessionKey,
        childSessionKey,
    };
}
function extractSessionKeys(input) {
    return [...new Set(input.match(SESSION_KEY_REGEX) ?? [])];
}
function firstPreview(obj, keys, maxLength) {
    for (const key of keys) {
        if (!(key in obj))
            continue;
        const preview = previewValue(obj[key], maxLength);
        if (preview)
            return preview;
    }
    return undefined;
}
function previewValue(input, maxLength) {
    if (input === undefined || input === null)
        return "";
    if (typeof input === "string")
        return truncateText(normalizeSpace(input), maxLength).text;
    if (typeof input === "number" || typeof input === "boolean")
        return String(input);
    try {
        return truncateText(normalizeSpace(JSON.stringify(input)), maxLength).text;
    }
    catch {
        return truncateText(normalizeSpace(String(input)), maxLength).text;
    }
}
function extractContent(obj) {
    const directKeys = [
        "content",
        "text",
        "message",
        "body",
        "prompt",
        "output",
        "value",
        "summary",
        "response",
    ];
    for (const key of directKeys) {
        const text = extractText(obj[key], 0);
        if (text)
            return truncateText(normalizeSpace(text), MAX_ENTRY_CONTENT_CHARS).text;
    }
    return "";
}
function extractText(input, depth) {
    if (depth > 4 || input === null || input === undefined)
        return "";
    if (typeof input === "string")
        return input;
    if (typeof input === "number" || typeof input === "boolean")
        return String(input);
    if (Array.isArray(input)) {
        const textBlocks = input
            .map((item) => extractStructuredTextBlock(item, depth + 1))
            .filter((item) => item.trim() !== "");
        if (textBlocks.length > 0) {
            return textBlocks.join(" ");
        }
        const thinkingBlocks = input
            .map((item) => extractStructuredThinkingBlock(item, depth + 1))
            .filter((item) => item.trim() !== "");
        if (thinkingBlocks.length > 0) {
            return thinkingBlocks.join(" ");
        }
        return input
            .map((item) => extractText(item, depth + 1))
            .filter((item) => item.trim() !== "")
            .join(" ");
    }
    const obj = asObject(input);
    if (!obj)
        return "";
    const structured = extractStructuredContentBlock(obj, depth);
    if (structured.trim() !== "")
        return structured;
    for (const key of ["text", "thinking", "content", "message", "body", "value", "summary", "output", "response"]) {
        const text = extractText(obj[key], depth + 1);
        if (text.trim() !== "")
            return text;
    }
    return "";
}
function extractStructuredContentBlock(input, depth) {
    return (extractStructuredTextBlock(input, depth) ||
        extractStructuredThinkingBlock(input, depth));
}
function extractStructuredTextBlock(input, depth) {
    const obj = asObject(input);
    if (!obj || depth > 4)
        return "";
    const blockType = (firstString(obj, ROLE_TYPE_KEYS) ?? "").toLowerCase();
    if (blockType === "text" || blockType === "summary_text") {
        return extractText(obj.text ?? obj.content ?? obj.value, depth + 1);
    }
    return "";
}
function extractStructuredThinkingBlock(input, depth) {
    const obj = asObject(input);
    if (!obj || depth > 4)
        return "";
    const blockType = (firstString(obj, ROLE_TYPE_KEYS) ?? "").toLowerCase();
    if (blockType === "thinking") {
        return extractText(obj.thinking ?? obj.text ?? obj.summary, depth + 1);
    }
    return "";
}
function extractRole(obj, messageObj) {
    for (const candidate of [messageObj, obj]) {
        if (!candidate)
            continue;
        const direct = firstString(candidate, ROLE_KEYS);
        if (direct)
            return direct;
        const roleLikeType = firstString(candidate, ROLE_TYPE_KEYS)?.toLowerCase();
        if (roleLikeType && KNOWN_ROLE_TYPES.has(roleLikeType)) {
            return roleLikeType;
        }
    }
    return undefined;
}
function extractAuthor(obj, messageObj) {
    return (messageObj ? firstString(messageObj, AUTHOR_KEYS) : undefined) ?? firstString(obj, AUTHOR_KEYS);
}
function extractTimestamp(obj, messageObj) {
    return normalizeTimestamp(firstValue(obj, TIME_KEYS) ?? firstValue(messageObj ?? {}, TIME_KEYS));
}
function extractEntryContent(obj, messageObj) {
    if (messageObj) {
        const nested = extractContent(messageObj);
        if (nested)
            return nested;
    }
    return extractContent(obj);
}
function normalizeHistoryFromText(raw) {
    if (!raw.trim())
        return [];
    return raw
        .split(/\r?\n/)
        .map((line) => normalizeSpace(line))
        .filter((line) => line !== "")
        .map((line) => parseHistoryEntry(line))
        .filter((item) => Boolean(item));
}
function pickLatestMessage(messages) {
    for (let idx = messages.length - 1; idx >= 0; idx -= 1) {
        const candidate = messages[idx];
        if (candidate.content.trim() !== "")
            return candidate;
    }
    return undefined;
}
function inferSessionExecutionChain(session, messages) {
    const fromHistory = inferSessionExecutionChainFromHistory(session, messages);
    if (fromHistory)
        return fromHistory;
    return inferSessionExecutionChainFromKey(session);
}
function inferSessionExecutionChainFromHistory(session, messages) {
    const acceptedEntries = messages.filter((message) => message.kind === "accepted");
    const spawnEntries = messages.filter((message) => message.kind === "spawn");
    if (acceptedEntries.length === 0 && spawnEntries.length === 0) {
        return undefined;
    }
    const acceptedEntry = acceptedEntries.at(-1);
    const spawnEntry = spawnEntries.at(-1);
    const fallbackFromKey = inferSessionExecutionChainFromKey(session);
    const accepted = acceptedEntries.length > 0 || spawnEntries.length > 0 || Boolean(fallbackFromKey?.accepted);
    const spawned = spawnEntries.length > 0 || Boolean(fallbackFromKey?.spawned);
    const acceptedAt = acceptedEntry?.timestamp ?? spawnEntry?.timestamp ?? fallbackFromKey?.acceptedAt;
    const spawnedAt = spawnEntry?.timestamp ?? fallbackFromKey?.spawnedAt;
    const parentSessionKey = spawnEntry?.parentSessionKey ??
        acceptedEntry?.parentSessionKey ??
        fallbackFromKey?.parentSessionKey ??
        (spawnEntries.length > 0 ? session.sessionKey : undefined);
    const childSessionKey = spawnEntry?.childSessionKey ??
        acceptedEntry?.childSessionKey ??
        fallbackFromKey?.childSessionKey ??
        (isRunSessionKey(session.sessionKey) ? session.sessionKey : undefined);
    const stage = resolveExecutionChainStage(session.state, accepted, spawned);
    const inferred = Boolean(acceptedEntry?.inferred) ||
        Boolean(spawnEntry?.inferred) ||
        (spawnEntries.length === 0 && Boolean(fallbackFromKey?.spawned)) ||
        (acceptedEntries.length === 0 && Boolean(fallbackFromKey?.accepted));
    return {
        accepted,
        spawned,
        acceptedAt,
        spawnedAt,
        parentSessionKey,
        childSessionKey,
        stage,
        source: "history",
        inferred,
        detail: buildExecutionChainDetail({
            session,
            accepted,
            spawned,
            acceptedAt,
            spawnedAt,
            parentSessionKey,
            childSessionKey,
            source: "history",
            inferred,
        }),
    };
}
function inferSessionExecutionChainFromKey(session) {
    const parentSessionKey = inferParentSessionKey(session.sessionKey);
    if (!parentSessionKey)
        return undefined;
    const accepted = true;
    const spawned = true;
    const stage = resolveExecutionChainStage(session.state, accepted, spawned);
    return {
        accepted,
        spawned,
        acceptedAt: session.lastMessageAt,
        spawnedAt: session.lastMessageAt,
        parentSessionKey,
        childSessionKey: session.sessionKey,
        stage,
        source: "session_key",
        inferred: true,
        detail: buildExecutionChainDetail({
            session,
            accepted,
            spawned,
            acceptedAt: session.lastMessageAt,
            spawnedAt: session.lastMessageAt,
            parentSessionKey,
            childSessionKey: session.sessionKey,
            source: "session_key",
            inferred: true,
        }),
    };
}
function resolveExecutionChainStage(sessionState, accepted, spawned) {
    if (sessionState === "running" || sessionState === "blocked" || sessionState === "waiting_approval" || sessionState === "error") {
        return "running";
    }
    if (spawned)
        return "spawned";
    if (accepted)
        return "accepted";
    return "idle";
}
function inferParentSessionKey(sessionKey) {
    const marker = ":run:";
    const markerIndex = sessionKey.indexOf(marker);
    if (markerIndex <= 0)
        return undefined;
    return sessionKey.slice(0, markerIndex);
}
function isRunSessionKey(sessionKey) {
    return inferParentSessionKey(sessionKey) !== undefined;
}
function buildExecutionChainDetail(input) {
    const parts = [];
    parts.push(`accepted=${input.accepted ? "yes" : "no"}`);
    parts.push(`spawned=${input.spawned ? "yes" : "no"}`);
    if (input.parentSessionKey)
        parts.push(`parent=${input.parentSessionKey}`);
    if (input.childSessionKey)
        parts.push(`child=${input.childSessionKey}`);
    if (input.acceptedAt)
        parts.push(`acceptedAt=${input.acceptedAt}`);
    if (input.spawnedAt)
        parts.push(`spawnedAt=${input.spawnedAt}`);
    parts.push(`source=${input.source}`);
    if (input.inferred)
        parts.push("inferred=yes");
    return parts.join(" | ");
}
function compareSessions(a, b) {
    const aTs = toMs(a.lastMessageAt);
    const bTs = toMs(b.lastMessageAt);
    if (aTs !== bTs)
        return bTs - aTs;
    return a.sessionKey.localeCompare(b.sessionKey);
}
function matchesSession(session, filters) {
    if (filters.state && session.state !== filters.state)
        return false;
    if (filters.agentId && (session.agentId ?? "").toLowerCase() !== filters.agentId.toLowerCase())
        return false;
    const q = filters.q?.trim().toLowerCase();
    if (!q)
        return true;
    return (session.sessionKey.toLowerCase().includes(q) ||
        (session.label ?? "").toLowerCase().includes(q) ||
        (session.agentId ?? "").toLowerCase().includes(q));
}
function normalizeTimestamp(value) {
    if (typeof value === "string") {
        const ms = Date.parse(value);
        if (!Number.isNaN(ms))
            return new Date(ms).toISOString();
        return undefined;
    }
    if (typeof value === "number" && Number.isFinite(value)) {
        return new Date(value).toISOString();
    }
    return undefined;
}
function firstString(obj, keys) {
    const value = firstValue(obj, keys);
    return typeof value === "string" && value.trim() !== "" ? value.trim() : undefined;
}
function firstValue(obj, keys) {
    for (const key of keys) {
        if (key in obj)
            return obj[key];
    }
    return undefined;
}
function summarizeSnippet(input) {
    const cleaned = normalizeSpace(input);
    if (cleaned.length <= MAX_SNIPPET_CHARS)
        return cleaned;
    return `${cleaned.slice(0, MAX_SNIPPET_CHARS - 3)}...`;
}
function normalizeSpace(input) {
    return input.replace(/\s+/g, " ").trim();
}
function truncateText(input, maxLength) {
    if (input.length <= maxLength) {
        return { text: input, truncated: false };
    }
    if (maxLength <= 3) {
        return { text: input.slice(0, Math.max(0, maxLength)), truncated: true };
    }
    return {
        text: `${input.slice(0, maxLength - 3)}...`,
        truncated: true,
    };
}
function toMs(value) {
    if (!value)
        return 0;
    const ms = Date.parse(value);
    return Number.isNaN(ms) ? 0 : ms;
}
function normalizePage(input) {
    if (!Number.isFinite(input))
        return 1;
    return Math.max(1, Math.trunc(input));
}
function normalizePageSize(input) {
    if (!Number.isFinite(input))
        return 20;
    return Math.max(1, Math.min(100, Math.trunc(input)));
}
function normalizeHistoryLimit(input, fallback = 8) {
    if (!Number.isFinite(input))
        return fallback;
    return Math.max(1, Math.min(200, Math.trunc(input)));
}
function asObject(v) {
    return v !== null && typeof v === "object" && !Array.isArray(v) ? v : undefined;
}
function asString(v) {
    return typeof v === "string" ? v : undefined;
}
