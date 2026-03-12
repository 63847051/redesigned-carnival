"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OpenClawLiveClient = void 0;
const node_child_process_1 = require("node:child_process");
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const node_util_1 = require("node:util");
const config_1 = require("../config");
const current_agent_catalog_1 = require("../runtime/current-agent-catalog");
const execFileAsync = (0, node_util_1.promisify)(node_child_process_1.execFile);
const ACTIVE_SESSION_STATES = new Set([
    "running",
    "active",
    "busy",
    "blocked",
    "waiting_approval",
    "working",
    "in_progress",
    "processing",
    "thinking",
    "executing",
    "streaming",
]);
const INACTIVE_SESSION_STATES = new Set([
    "idle",
    "inactive",
    "error",
    "failed",
    "stopped",
    "stopping",
    "closed",
    "done",
    "completed",
    "complete",
    "paused",
    "aborted",
    "terminated",
    "cancelled",
    "canceled",
]);
const FALLBACK_ACTIVE_RECENCY_WINDOW_MS = 45 * 60 * 1000;
/**
 * Live read client using official OpenClaw CLI JSON outputs.
 * Read-only by design: only list/status commands are used.
 */
class OpenClawLiveClient {
    sessionCache = new Map();
    sessionFileCache = new Map();
    async sessionsList() {
        const openclawHome = (0, current_agent_catalog_1.resolveOpenClawHomePath)();
        const configuredAgentKeys = await this.loadConfiguredAgentKeys();
        let data;
        try {
            data = await runJson([
                "sessions",
                "--json",
            ]);
        }
        catch {
            return this.loadSessionsFromStores();
        }
        const cliSessions = (data.sessions ?? []).map((item) => ({
            key: asString(item.key),
            sessionKey: asString(item.key),
            sessionId: asString(item.sessionId),
            agentId: asString(item.agentId),
            updatedAtMs: asNumber(item.updatedAt),
            sessionFile: asString(item.sessionFile) ??
                buildSessionFilePath(openclawHome, asString(item.agentId), asString(item.sessionId)),
            model: asString(item.model),
            inputTokens: asNumber(item.inputTokens),
            outputTokens: asNumber(item.outputTokens),
            totalTokens: asNumber(item.totalTokens),
            state: readSessionState(item),
            active: asBoolean(item.active) ?? false,
        })).filter((item) => matchesConfiguredAgents(item.agentId ?? extractAgentIdFromSessionKey(item.sessionKey), configuredAgentKeys));
        let sessions = cliSessions;
        try {
            const storeSessions = (await this.loadSessionsFromStores()).sessions ?? [];
            sessions = mergeSessionLists(cliSessions, storeSessions);
        }
        catch {
            sessions = cliSessions;
        }
        this.sessionCache.clear();
        for (const s of sessions) {
            if (!s.sessionKey)
                continue;
            this.sessionCache.set(s.sessionKey, {
                model: s.model,
                inputTokens: s.inputTokens,
                outputTokens: s.outputTokens,
                totalTokens: s.totalTokens,
                sessionFile: s.sessionFile,
            });
        }
        return { sessions };
    }
    async sessionStatus(sessionKey) {
        const cached = this.sessionCache.get(sessionKey);
        const rawText = cached
            ? `Model: ${cached.model ?? "unknown"}\nTokens: ${cached.inputTokens ?? 0} in / ${cached.outputTokens ?? 0} out\nTotal: ${cached.totalTokens ?? 0}`
            : "";
        return { rawText };
    }
    async sessionsHistory(request) {
        const sessionKey = request.sessionKey.trim();
        if (!sessionKey) {
            return { rawText: "" };
        }
        const limit = normalizeLimit(request.limit);
        let sessionFile = this.sessionCache.get(sessionKey)?.sessionFile;
        if (!sessionFile) {
            sessionFile = await this.lookupSessionFile(sessionKey);
        }
        if (sessionFile) {
            const fromFile = await readSessionHistoryFile(sessionFile, limit);
            if (fromFile)
                return fromFile;
        }
        const attempts = [
            ["sessions", "history", sessionKey, "--json", "--limit", String(limit)],
            ["sessions", "history", sessionKey, "--limit", String(limit), "--json"],
            ["sessions", "history", sessionKey, "--json"],
        ];
        for (const args of attempts) {
            try {
                const json = await runJson(args);
                return {
                    json,
                    rawText: JSON.stringify(json),
                };
            }
            catch {
                continue;
            }
        }
        try {
            const rawText = await runHistoryText(sessionKey, limit);
            return normalizeRawHistoryText(rawText, limit);
        }
        catch {
            return { rawText: "" };
        }
    }
    async cronList() {
        let data;
        try {
            data = await runJson(["cron", "list", "--json"], { timeoutMs: 2_500 });
        }
        catch {
            return { jobs: [] };
        }
        const jobs = (data.jobs ?? []).map((job) => ({
            id: asString(job.id),
            name: asString(job.name),
            enabled: asBoolean(job.enabled),
            state: asObject(job.state)
                ? {
                    nextRunAtMs: asNumber(asObject(job.state)?.nextRunAtMs),
                }
                : undefined,
        }));
        return { jobs };
    }
    async approvalsGet() {
        try {
            const json = await runJson(["approvals", "get", "--json"], { timeoutMs: 2_500 });
            return {
                json,
                rawText: JSON.stringify(json),
            };
        }
        catch {
            try {
                const rawText = await runText(["approvals", "get"], { timeoutMs: 1_500 });
                return { rawText };
            }
            catch {
                return { rawText: "" };
            }
        }
    }
    async approvalsApprove(request) {
        assertApprovalActionsEnabled("approve");
        const args = ["approvals", "approve", request.approvalId];
        if (request.reason)
            args.push("--reason", request.reason);
        const rawText = await runText(args);
        return {
            ok: true,
            action: "approve",
            approvalId: request.approvalId,
            reason: request.reason,
            rawText,
        };
    }
    async approvalsReject(request) {
        assertApprovalActionsEnabled("reject");
        const args = ["approvals", "reject", request.approvalId, "--reason", request.reason];
        const rawText = await runText(args);
        return {
            ok: true,
            action: "reject",
            approvalId: request.approvalId,
            reason: request.reason,
            rawText,
        };
    }
    async loadSessionsFromStores() {
        const openclawHome = (0, current_agent_catalog_1.resolveOpenClawHomePath)();
        const agentsPath = (0, node_path_1.join)(openclawHome, "agents");
        const configuredAgentKeys = await this.loadConfiguredAgentKeys();
        let agentDirs = [];
        try {
            const entries = await (0, promises_1.readdir)(agentsPath, { withFileTypes: true });
            agentDirs = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name);
        }
        catch {
            return { sessions: [] };
        }
        if (configuredAgentKeys.size > 0) {
            agentDirs = agentDirs.filter((agentId) => matchesConfiguredAgents(agentId, configuredAgentKeys));
        }
        const sessions = [];
        for (const agentId of agentDirs) {
            const sessionsPath = (0, node_path_1.join)(agentsPath, agentId, "sessions", "sessions.json");
            try {
                const parsed = JSON.parse(await (0, promises_1.readFile)(sessionsPath, "utf8"));
                const records = extractSessionRecords(parsed);
                for (const record of records) {
                    const sessionKey = asString(record.key) ?? asString(record.sessionKey);
                    if (!sessionKey)
                        continue;
                    const updatedAtMs = readUpdatedAtMs(record);
                    sessions.push({
                        key: sessionKey,
                        sessionKey,
                        sessionId: asString(record.sessionId),
                        agentId: asString(record.agentId) ?? agentId,
                        updatedAtMs: Number.isFinite(updatedAtMs) ? updatedAtMs : undefined,
                        sessionFile: asString(record.sessionFile) ??
                            buildSessionFilePath(openclawHome, asString(record.agentId) ?? agentId, asString(record.sessionId)),
                        model: asString(record.model),
                        inputTokens: asNumber(record.inputTokens),
                        outputTokens: asNumber(record.outputTokens),
                        totalTokens: asNumber(record.totalTokens),
                        state: readSessionState(record),
                        active: isSessionActive(record, updatedAtMs),
                    });
                }
            }
            catch {
                continue;
            }
        }
        sessions.sort((a, b) => (b.updatedAtMs ?? 0) - (a.updatedAtMs ?? 0));
        this.sessionCache.clear();
        for (const session of sessions) {
            if (!session.sessionKey)
                continue;
            this.sessionCache.set(session.sessionKey, {
                model: session.model,
                inputTokens: session.inputTokens,
                outputTokens: session.outputTokens,
                totalTokens: session.totalTokens,
                sessionFile: session.sessionFile,
            });
            if (session.sessionFile) {
                this.sessionFileCache.set(session.sessionKey, session.sessionFile);
            }
        }
        return { sessions };
    }
    async lookupSessionFile(sessionKey) {
        const cached = this.sessionFileCache.get(sessionKey);
        if (cached)
            return cached;
        const openclawHome = (0, current_agent_catalog_1.resolveOpenClawHomePath)();
        const agentsPath = (0, node_path_1.join)(openclawHome, "agents");
        const configuredAgentKeys = await this.loadConfiguredAgentKeys();
        if (!matchesConfiguredAgents(extractAgentIdFromSessionKey(sessionKey), configuredAgentKeys)) {
            return undefined;
        }
        let agentDirs = [];
        try {
            const entries = await (0, promises_1.readdir)(agentsPath, { withFileTypes: true });
            agentDirs = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name);
        }
        catch {
            return undefined;
        }
        if (configuredAgentKeys.size > 0) {
            agentDirs = agentDirs.filter((agentId) => matchesConfiguredAgents(agentId, configuredAgentKeys));
        }
        for (const agentId of agentDirs) {
            const sessionsPath = (0, node_path_1.join)(agentsPath, agentId, "sessions", "sessions.json");
            try {
                const parsed = JSON.parse(await (0, promises_1.readFile)(sessionsPath, "utf8"));
                for (const record of extractSessionRecords(parsed)) {
                    const key = asString(record.key) ?? asString(record.sessionKey);
                    const sessionFile = asString(record.sessionFile) ??
                        buildSessionFilePath(openclawHome, asString(record.agentId) ?? agentId, asString(record.sessionId));
                    if (!key || !sessionFile)
                        continue;
                    this.sessionFileCache.set(key, sessionFile);
                }
            }
            catch {
                continue;
            }
        }
        return this.sessionFileCache.get(sessionKey);
    }
    async loadConfiguredAgentKeys() {
        const catalog = await (0, current_agent_catalog_1.loadCurrentAgentCatalog)();
        return new Set(catalog.entries.map((entry) => normalizeAgentKey(entry.agentId)));
    }
}
exports.OpenClawLiveClient = OpenClawLiveClient;
async function runJson(args, options) {
    const stdout = await runText(args, options);
    return JSON.parse(stdout);
}
async function runText(args, options) {
    const { stdout } = await execFileAsync("openclaw", args, {
        timeout: options?.timeoutMs ?? 20_000,
        maxBuffer: options?.maxBuffer ?? 2 * 1024 * 1024,
    });
    return stdout;
}
async function runHistoryText(sessionKey, limit) {
    try {
        return await runText(["sessions", "history", sessionKey, "--limit", String(limit)]);
    }
    catch (error) {
        if (!isUnknownLimitOptionError(error))
            throw error;
    }
    const rawText = await runText(["sessions", "history", sessionKey]);
    const trimmed = rawText.trim();
    if (trimmed === "")
        return rawText;
    const lines = trimmed.split(/\r?\n/);
    return lines.slice(-limit).join("\n");
}
function normalizeRawHistoryText(rawText, limit) {
    const trimmed = rawText.trim();
    if (trimmed === "")
        return { rawText };
    const lines = trimmed.split(/\r?\n/).map((line) => line.trim()).filter((line) => line !== "");
    const jsonLike = lines.every((line) => line.startsWith("{") || line.startsWith("["));
    if (jsonLike) {
        return normalizeSessionHistoryChunk(lines.join("\n"), limit);
    }
    return { rawText };
}
function isUnknownLimitOptionError(error) {
    if (!(error instanceof Error))
        return false;
    return /unknown option '--limit'/.test(error.message);
}
function asString(v) {
    return typeof v === "string" ? v : undefined;
}
function asNumber(v) {
    return typeof v === "number" ? v : undefined;
}
function asBoolean(v) {
    return typeof v === "boolean" ? v : undefined;
}
function asObject(v) {
    return v !== null && typeof v === "object" ? v : undefined;
}
function normalizeLimit(input) {
    if (typeof input !== "number" || !Number.isFinite(input))
        return 12;
    return Math.max(1, Math.min(200, Math.trunc(input)));
}
async function readSessionHistoryFile(sessionFile, limit) {
    try {
        const { stdout } = await execFileAsync("tail", ["-n", String(Math.max(limit * 8, 80)), sessionFile], {
            timeout: 5_000,
            maxBuffer: 512 * 1024,
        });
        return normalizeSessionHistoryChunk(stdout, limit);
    }
    catch {
        try {
            const raw = await (0, promises_1.readFile)(sessionFile, "utf8");
            return normalizeSessionHistoryChunk(raw, limit);
        }
        catch {
            return undefined;
        }
    }
}
function normalizeSessionHistoryChunk(raw, limit) {
    const lines = raw
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter((line) => line !== "");
    if (lines.length === 0)
        return { rawText: "" };
    const recentLines = lines.slice(-limit);
    const history = recentLines.map((line) => {
        try {
            return JSON.parse(line);
        }
        catch {
            return line;
        }
    });
    return {
        json: { history },
        rawText: recentLines.join("\n"),
    };
}
function extractSessionRecords(parsed) {
    if (Array.isArray(parsed))
        return parsed.flatMap((item) => (asObject(item) ? [item] : []));
    const root = asObject(parsed);
    if (!root)
        return [];
    const nestedCollections = [root.sessions, root.items, root.records];
    for (const collection of nestedCollections) {
        if (!Array.isArray(collection))
            continue;
        const records = collection.flatMap((item) => (asObject(item) ? [item] : []));
        if (records.length > 0)
            return records;
    }
    return Object.entries(root).flatMap(([key, value]) => {
        const record = asObject(value);
        if (!record)
            return [];
        return [{ key, ...record }];
    });
}
function mergeSessionLists(primary = [], secondary = []) {
    const merged = new Map();
    const mergeItem = (item) => {
        const sessionKey = item.sessionKey ?? item.key;
        if (!sessionKey)
            return;
        const current = merged.get(sessionKey);
        if (!current) {
            merged.set(sessionKey, item);
            return;
        }
        merged.set(sessionKey, {
            ...current,
            ...item,
            sessionKey,
            key: item.key ?? current.key ?? sessionKey,
            sessionFile: item.sessionFile ?? current.sessionFile,
            sessionId: item.sessionId ?? current.sessionId,
            agentId: item.agentId ?? current.agentId,
            updatedAtMs: Math.max(current.updatedAtMs ?? 0, item.updatedAtMs ?? 0) || undefined,
            active: item.active ?? current.active ?? false,
            state: item.state ?? current.state,
            model: item.model ?? current.model,
            inputTokens: item.inputTokens ?? current.inputTokens,
            outputTokens: item.outputTokens ?? current.outputTokens,
            totalTokens: item.totalTokens ?? current.totalTokens,
        });
    };
    for (const item of secondary)
        mergeItem(item);
    for (const item of primary)
        mergeItem(item);
    return [...merged.values()].sort((a, b) => (b.updatedAtMs ?? 0) - (a.updatedAtMs ?? 0));
}
function isSessionActive(item, updatedAtMs) {
    const explicitActive = asBoolean(item.active) ?? asBoolean(item.isActive);
    if (typeof explicitActive === "boolean")
        return explicitActive;
    const explicitState = readSessionState(item);
    if (explicitState) {
        if (ACTIVE_SESSION_STATES.has(explicitState))
            return true;
        if (INACTIVE_SESSION_STATES.has(explicitState))
            return false;
    }
    if (!Number.isFinite(updatedAtMs))
        return false;
    return Date.now() - updatedAtMs <= FALLBACK_ACTIVE_RECENCY_WINDOW_MS;
}
function readSessionState(item) {
    const direct = asString(item.state) ??
        asString(item.status) ??
        asString(item.runState) ??
        asString(item.lifecycleState);
    if (direct)
        return direct.trim().toLowerCase();
    const acp = asObject(item.acp);
    const acpState = asString(acp?.state);
    return acpState ? acpState.trim().toLowerCase() : undefined;
}
function readUpdatedAtMs(item) {
    const candidates = [
        item.updatedAt,
        item.lastActivityAt,
        item.createdAt,
        asObject(item.acp)?.lastActivityAt,
        asObject(item.acp)?.updatedAt,
        asObject(item.acp)?.createdAt,
    ];
    for (const candidate of candidates) {
        if (typeof candidate === "number" && Number.isFinite(candidate))
            return normalizeEpochMs(candidate);
        if (typeof candidate === "string" && candidate.trim() !== "") {
            const trimmed = candidate.trim();
            if (/^\d+(\.\d+)?$/.test(trimmed)) {
                const numeric = Number(trimmed);
                if (Number.isFinite(numeric))
                    return normalizeEpochMs(numeric);
            }
            const parsed = Date.parse(trimmed);
            if (!Number.isNaN(parsed))
                return parsed;
        }
    }
    return Number.NaN;
}
function normalizeEpochMs(value) {
    const abs = Math.abs(value);
    if (abs >= 1e14)
        return value / 1000;
    if (abs > 0 && abs < 1e12)
        return value * 1000;
    return value;
}
function buildSessionFilePath(openclawHome, agentId, sessionId) {
    if (!agentId || !sessionId)
        return undefined;
    return (0, node_path_1.join)(openclawHome, "agents", agentId, "sessions", `${sessionId}.jsonl`);
}
function extractAgentIdFromSessionKey(sessionKey) {
    const value = sessionKey?.trim();
    if (!value)
        return undefined;
    const match = /^agent:([^:]+):/i.exec(value);
    return match?.[1];
}
function matchesConfiguredAgents(agentId, configuredAgentKeys) {
    if (configuredAgentKeys.size === 0)
        return true;
    const normalized = normalizeAgentKey(agentId);
    return normalized.length > 0 && configuredAgentKeys.has(normalized);
}
function normalizeAgentKey(agentId) {
    return agentId?.trim().toLowerCase() ?? "";
}
function assertApprovalActionsEnabled(action) {
    if (config_1.APPROVAL_ACTIONS_ENABLED)
        return;
    throw new Error(`approvals ${action} is disabled by safety gate (APPROVAL_ACTIONS_ENABLED=${String(config_1.APPROVAL_ACTIONS_ENABLED)}).`);
}
