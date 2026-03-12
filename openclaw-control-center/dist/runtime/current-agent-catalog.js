"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadCurrentAgentCatalog = loadCurrentAgentCatalog;
exports.resolveOpenClawHomePath = resolveOpenClawHomePath;
exports.resolveOpenClawConfigPath = resolveOpenClawConfigPath;
const promises_1 = require("node:fs/promises");
const node_os_1 = require("node:os");
const node_path_1 = require("node:path");
async function loadCurrentAgentCatalog() {
    const sourcePath = resolveOpenClawConfigPath();
    try {
        const raw = JSON.parse(await (0, promises_1.readFile)(sourcePath, "utf8"));
        const root = asObject(raw) ?? {};
        const agents = asObject(root.agents) ?? {};
        const list = asArray(agents.list);
        const merged = new Map();
        for (const item of list) {
            const obj = asObject(item);
            if (!obj)
                continue;
            const agentId = asString(obj.id)?.trim() ?? asString(obj.name)?.trim();
            if (!agentId)
                continue;
            const key = normalizeKey(agentId);
            if (merged.has(key))
                continue;
            merged.set(key, {
                agentId,
                displayName: asString(obj.name)?.trim() || agentId,
            });
        }
        const entries = [...merged.values()].sort((a, b) => a.agentId.localeCompare(b.agentId));
        if (entries.length === 0) {
            return {
                status: "partial",
                sourcePath,
                detail: "openclaw.json found but agents.list is empty.",
                entries: [],
            };
        }
        return {
            status: "connected",
            sourcePath,
            detail: `loaded ${entries.length} current agent(s) from openclaw.json.`,
            entries,
        };
    }
    catch (error) {
        if (isFsNotFound(error)) {
            return {
                status: "not_connected",
                sourcePath,
                detail: "openclaw.json not found.",
                entries: [],
            };
        }
        return {
            status: "partial",
            sourcePath,
            detail: "openclaw.json exists but could not be parsed.",
            entries: [],
        };
    }
}
function resolveOpenClawHomePath() {
    return process.env.OPENCLAW_HOME?.trim() || (0, node_path_1.join)((0, node_os_1.homedir)(), ".openclaw");
}
function resolveOpenClawConfigPath() {
    const explicit = process.env.OPENCLAW_CONFIG_PATH?.trim();
    if (explicit)
        return explicit;
    return (0, node_path_1.join)(resolveOpenClawHomePath(), "openclaw.json");
}
function isFsNotFound(error) {
    return Boolean(error &&
        typeof error === "object" &&
        "code" in error &&
        typeof error.code === "string" &&
        error.code === "ENOENT");
}
function normalizeKey(input) {
    return input.trim().toLowerCase();
}
function asObject(input) {
    return input !== null && typeof input === "object" && !Array.isArray(input)
        ? input
        : undefined;
}
function asArray(input) {
    return Array.isArray(input) ? input : [];
}
function asString(input) {
    return typeof input === "string" ? input : undefined;
}
