"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadBestEffortAgentRoster = loadBestEffortAgentRoster;
const node_path_1 = require("node:path");
const promises_1 = require("node:fs/promises");
const current_agent_catalog_1 = require("./current-agent-catalog");
async function loadBestEffortAgentRoster() {
    const homePath = (0, current_agent_catalog_1.resolveOpenClawHomePath)();
    const sourcePath = (0, current_agent_catalog_1.resolveOpenClawConfigPath)();
    const runtimeAgentsPath = (0, node_path_1.join)(homePath, "agents");
    const fromConfig = await (0, current_agent_catalog_1.loadCurrentAgentCatalog)();
    if (fromConfig.entries.length > 0) {
        return {
            status: "connected",
            sourcePath,
            detail: `${fromConfig.detail} openclaw.json is treated as the current-project source of truth; runtime folders are ignored for roster discovery.`,
            entries: fromConfig.entries.map((entry) => ({
                agentId: entry.agentId,
                displayName: entry.displayName,
            })),
        };
    }
    const fromRuntime = await loadRosterFromRuntimeDirs(runtimeAgentsPath);
    const status = resolveMergedStatus(fromConfig.status, fromRuntime.status, fromRuntime.entries.length);
    const detail = `Config: ${fromConfig.detail} Runtime: ${fromRuntime.detail} Using runtime fallback: ${fromRuntime.entries.length} agent(s).`;
    return {
        status,
        sourcePath,
        detail,
        entries: fromRuntime.entries,
    };
}
async function loadRosterFromRuntimeDirs(runtimeAgentsPath) {
    try {
        const dirEntries = await (0, promises_1.readdir)(runtimeAgentsPath, { withFileTypes: true });
        const entries = dirEntries
            .filter((entry) => entry.isDirectory())
            .map((entry) => ({
            agentId: entry.name,
            displayName: entry.name,
        }));
        if (entries.length === 0) {
            return {
                status: "partial",
                detail: "runtime agents directory found but empty.",
                entries: [],
            };
        }
        return {
            status: "connected",
            detail: `loaded ${entries.length} agent folder(s) from runtime.`,
            entries,
        };
    }
    catch (error) {
        if (isFsNotFound(error)) {
            return {
                status: "not_connected",
                detail: "runtime agents directory not found.",
                entries: [],
            };
        }
        return {
            status: "partial",
            detail: "runtime agents directory exists but could not be read.",
            entries: [],
        };
    }
}
function resolveMergedStatus(configStatus, runtimeStatus, totalEntries) {
    if (totalEntries === 0) {
        return configStatus === "not_connected" && runtimeStatus === "not_connected"
            ? "not_connected"
            : "partial";
    }
    if (configStatus === "partial" || runtimeStatus === "partial")
        return "partial";
    return "connected";
}
function isFsNotFound(error) {
    return Boolean(error &&
        typeof error === "object" &&
        "code" in error &&
        typeof error.code === "string" &&
        error.code === "ENOENT");
}
