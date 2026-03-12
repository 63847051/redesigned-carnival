"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.runMonitorOnce = runMonitorOnce;
exports.monitorIntervalMs = monitorIntervalMs;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const config_1 = require("../config");
const commander_1 = require("./commander");
const commander_digest_1 = require("./commander-digest");
const diff_summary_1 = require("./diff-summary");
const snapshot_store_1 = require("./snapshot-store");
const task_heartbeat_1 = require("./task-heartbeat");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
const TIMELINE_LOG = (0, node_path_1.join)(RUNTIME_DIR, "timeline.log");
async function runMonitorOnce(adapter) {
    const snapshot = await adapter.snapshot();
    const stored = await (0, snapshot_store_1.saveSnapshot)(snapshot);
    const alerts = (0, commander_1.commanderAlerts)(snapshot);
    const digest = await (0, commander_digest_1.writeCommanderDigest)(snapshot, alerts);
    const heartbeat = await (0, task_heartbeat_1.runTaskHeartbeat)();
    const heartbeatSummary = `heartbeat=${heartbeat.mode}:${heartbeat.executed}/${heartbeat.selected}`;
    await (0, promises_1.mkdir)(RUNTIME_DIR, { recursive: true });
    await (0, promises_1.appendFile)(TIMELINE_LOG, `${new Date().toISOString()} | ${(0, diff_summary_1.formatDiffSummary)(stored.diff)} | alerts=${alerts.length} | ${heartbeatSummary}\n`, "utf8");
    console.log("[mission-control] monitor", {
        diffSummary: (0, diff_summary_1.formatDiffSummary)(stored.diff),
        alerts,
        heartbeat,
        timelineLog: TIMELINE_LOG,
        digestJson: digest.jsonPath,
        digestMarkdown: digest.markdownPath,
    });
}
function monitorIntervalMs() {
    return config_1.POLLING_INTERVALS_MS.sessionsList;
}
