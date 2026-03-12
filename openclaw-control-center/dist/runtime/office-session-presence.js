"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadBestEffortOfficeSessionPresence = loadBestEffortOfficeSessionPresence;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const current_agent_catalog_1 = require("./current-agent-catalog");
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
const ACTIVE_RECENCY_WINDOWS_MS = resolveActiveRecencyWindowsMs();
async function loadBestEffortOfficeSessionPresence() {
    const openclawHome = (0, current_agent_catalog_1.resolveOpenClawHomePath)();
    const agentsPath = (0, node_path_1.join)(openclawHome, "agents");
    const sourcePath = (0, node_path_1.join)(agentsPath, "*/sessions/sessions.json");
    const currentCatalog = await (0, current_agent_catalog_1.loadCurrentAgentCatalog)();
    const configuredAgentKeys = new Set(currentCatalog.entries.map((entry) => normalizeAgentKey(entry.agentId)));
    let agentDirs = [];
    try {
        const entries = await (0, promises_1.readdir)(agentsPath, { withFileTypes: true });
        agentDirs = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name);
    }
    catch (error) {
        if (!isFsNotFound(error)) {
            return {
                status: "partial",
                sourcePath,
                detail: "Runtime agent directory exists but could not be read cleanly.",
                activeSessionsByAgent: new Map(),
                totalActiveSessions: 0,
            };
        }
        return {
            status: "not_connected",
            sourcePath,
            detail: "Runtime agent directory not found.",
            activeSessionsByAgent: new Map(),
            totalActiveSessions: 0,
        };
    }
    if (configuredAgentKeys.size > 0) {
        agentDirs = agentDirs.filter((agentId) => configuredAgentKeys.has(normalizeAgentKey(agentId)));
    }
    if (agentDirs.length === 0) {
        return {
            status: "not_connected",
            sourcePath,
            detail: configuredAgentKeys.size > 0
                ? "No runtime session stores were found for the current configured agents."
                : "Runtime agent directory is empty.",
            activeSessionsByAgent: new Map(),
            totalActiveSessions: 0,
        };
    }
    const recordsByAgent = new Map();
    let parsedStores = 0;
    let parseErrors = 0;
    for (const agentId of agentDirs) {
        const sessionsPath = (0, node_path_1.join)(agentsPath, agentId, "sessions", "sessions.json");
        try {
            const parsed = JSON.parse(await (0, promises_1.readFile)(sessionsPath, "utf8"));
            parsedStores += 1;
            const records = extractSessionRecords(parsed);
            recordsByAgent.set(agentId, records);
        }
        catch (error) {
            if (isFsNotFound(error))
                continue;
            parseErrors += 1;
        }
    }
    let selectedWindowMs = ACTIVE_RECENCY_WINDOWS_MS[0] ?? 45 * 60 * 1000;
    let selectedActiveByAgent = new Map();
    let totalActiveSessions = 0;
    const nowMs = Date.now();
    for (const windowMs of ACTIVE_RECENCY_WINDOWS_MS) {
        const activeByAgent = deriveActiveSessionsByAgent(recordsByAgent, windowMs, nowMs);
        const total = [...activeByAgent.values()].reduce((sum, value) => sum + value, 0);
        selectedWindowMs = windowMs;
        selectedActiveByAgent = activeByAgent;
        totalActiveSessions = total;
        if (total > 0)
            break;
    }
    const usedAdaptiveFallback = totalActiveSessions > 0 &&
        selectedWindowMs !== (ACTIVE_RECENCY_WINDOWS_MS[0] ?? selectedWindowMs);
    if (parsedStores === 0 && parseErrors === 0) {
        return {
            status: "not_connected",
            sourcePath,
            detail: "No runtime session stores found.",
            activeSessionsByAgent: selectedActiveByAgent,
            totalActiveSessions,
        };
    }
    const status = parseErrors > 0 ? "partial" : "connected";
    return {
        status,
        sourcePath,
        detail: `Derived ${totalActiveSessions} active session(s) from ${parsedStores} session store(s)` +
            ` using state + ${Math.round(selectedWindowMs / 60000)}m recency window.` +
            (configuredAgentKeys.size > 0 ? ` Filtered to ${configuredAgentKeys.size} configured current agent(s).` : "") +
            (usedAdaptiveFallback
                ? ` Window auto-expanded from ${Math.round((ACTIVE_RECENCY_WINDOWS_MS[0] ?? selectedWindowMs) / 60000)}m after an all-zero pass.`
                : "") +
            (parseErrors > 0 ? ` ${parseErrors} store(s) could not be parsed.` : ""),
        activeSessionsByAgent: selectedActiveByAgent,
        totalActiveSessions,
    };
}
function deriveActiveSessionsByAgent(recordsByAgent, recencyWindowMs, nowMs) {
    const activeByAgent = new Map();
    for (const [agentId, records] of recordsByAgent.entries()) {
        let active = 0;
        for (const item of records) {
            if (isSessionActive(item, recencyWindowMs, nowMs))
                active += 1;
        }
        if (active > 0)
            activeByAgent.set(agentId, active);
    }
    return activeByAgent;
}
function isSessionActive(item, recencyWindowMs, nowMs) {
    const explicitActive = readExplicitActiveFlag(item);
    if (typeof explicitActive === "boolean")
        return explicitActive;
    const explicitState = readSessionState(item);
    if (explicitState) {
        if (ACTIVE_SESSION_STATES.has(explicitState))
            return true;
        if (INACTIVE_SESSION_STATES.has(explicitState))
            return false;
    }
    const updatedAtMs = readUpdatedAtMs(item);
    if (!Number.isFinite(updatedAtMs))
        return false;
    return nowMs - updatedAtMs <= recencyWindowMs;
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
function readExplicitActiveFlag(item) {
    const direct = asBoolean(item.active) ?? asBoolean(item.isActive);
    if (typeof direct === "boolean")
        return direct;
    const acp = asObject(item.acp);
    const acpActive = asBoolean(acp?.active) ?? asBoolean(acp?.isActive);
    return typeof acpActive === "boolean" ? acpActive : undefined;
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
                const parsedNumeric = Number(trimmed);
                if (Number.isFinite(parsedNumeric))
                    return normalizeEpochMs(parsedNumeric);
            }
            const parsedDate = Date.parse(trimmed);
            if (!Number.isNaN(parsedDate))
                return parsedDate;
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
function extractSessionRecords(parsed) {
    const direct = normalizeRecordCollection(parsed).filter(looksLikeSessionRecord);
    if (direct.length > 0)
        return direct;
    const root = asObject(parsed);
    if (!root)
        return [];
    const topLevelCollections = [
        normalizeRecordCollection(root.sessions),
        normalizeRecordCollection(root.items),
        normalizeRecordCollection(root.records),
    ];
    for (const collection of topLevelCollections) {
        const records = collection.filter(looksLikeSessionRecord);
        if (records.length > 0)
            return records;
    }
    const data = asObject(root.data);
    if (data) {
        const nestedCollections = [
            normalizeRecordCollection(data.sessions),
            normalizeRecordCollection(data.items),
            normalizeRecordCollection(data.records),
        ];
        for (const collection of nestedCollections) {
            const records = collection.filter(looksLikeSessionRecord);
            if (records.length > 0)
                return records;
        }
    }
    return [];
}
function normalizeRecordCollection(input) {
    if (Array.isArray(input)) {
        return input
            .map((item) => asObject(item))
            .filter((item) => Boolean(item));
    }
    const object = asObject(input);
    if (!object)
        return [];
    return Object.values(object)
        .map((item) => asObject(item))
        .filter((item) => Boolean(item));
}
function looksLikeSessionRecord(item) {
    if (asString(item.sessionId) ||
        asString(item.sessionKey) ||
        asString(item.key) ||
        asString(item.sessionFile)) {
        return true;
    }
    if (asObject(item.acp) || asObject(item.origin) || asObject(item.deliveryContext))
        return true;
    if (readSessionState(item))
        return true;
    return false;
}
function resolveActiveRecencyWindowsMs() {
    const fallbackMinutes = [45, 180, 720, 1440];
    const rawMinutes = process.env.OFFICE_SESSION_ACTIVE_WINDOW_MINUTES;
    if (!rawMinutes)
        return fallbackMinutes.map((minutes) => minutes * 60 * 1000);
    const parsedMinutes = rawMinutes
        .split(",")
        .map((item) => Number(item.trim()))
        .filter((item) => Number.isFinite(item) && item > 0)
        .map((item) => Math.max(1, Math.trunc(item)));
    if (parsedMinutes.length === 0)
        return fallbackMinutes.map((minutes) => minutes * 60 * 1000);
    const deduped = [];
    for (const minutes of parsedMinutes) {
        if (!deduped.includes(minutes))
            deduped.push(minutes);
    }
    return deduped.map((minutes) => minutes * 60 * 1000);
}
function isFsNotFound(error) {
    return Boolean(error &&
        typeof error === "object" &&
        "code" in error &&
        typeof error.code === "string" &&
        error.code === "ENOENT");
}
function normalizeAgentKey(input) {
    return input.trim().toLowerCase();
}
function asObject(input) {
    return input !== null && typeof input === "object" && !Array.isArray(input)
        ? input
        : undefined;
}
function asString(input) {
    return typeof input === "string" ? input : undefined;
}
function asBoolean(input) {
    return typeof input === "boolean" ? input : undefined;
}
