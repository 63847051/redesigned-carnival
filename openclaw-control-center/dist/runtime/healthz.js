"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildHealthzPayload = buildHealthzPayload;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const config_1 = require("../config");
const monitor_health_1 = require("./monitor-health");
const PACKAGE_JSON_PATH = (0, node_path_1.join)(process.cwd(), "package.json");
const DIST_INDEX_PATH = (0, node_path_1.join)(process.cwd(), "dist", "index.js");
async function buildHealthzPayload(snapshot, now = new Date()) {
    const monitor = await (0, monitor_health_1.readMonitorLagSummary)(config_1.POLLING_INTERVALS_MS.sessionsList, now);
    const [build, snapshotFreshness] = await Promise.all([
        readBuildInfo(),
        computeSnapshotFreshness(snapshot, config_1.POLLING_INTERVALS_MS.sessionsList, now),
    ]);
    const status = resolveOverallStatus(snapshotFreshness.status, monitor.status);
    return {
        generatedAt: now.toISOString(),
        status,
        build,
        snapshot: snapshotFreshness,
        monitor,
    };
}
async function readBuildInfo() {
    let name = "unknown";
    let version = "0.0.0";
    try {
        const raw = await (0, promises_1.readFile)(PACKAGE_JSON_PATH, "utf8");
        const pkg = JSON.parse(raw);
        if (typeof pkg.name === "string" && pkg.name.trim())
            name = pkg.name;
        if (typeof pkg.version === "string" && pkg.version.trim())
            version = pkg.version;
    }
    catch {
        // keep defaults
    }
    let distBuiltAt;
    try {
        const stats = await (0, promises_1.stat)(DIST_INDEX_PATH);
        distBuiltAt = stats.mtime.toISOString();
    }
    catch {
        distBuiltAt = undefined;
    }
    return {
        name,
        version,
        node: process.version,
        readonlyMode: config_1.READONLY_MODE,
        approvalActionsEnabled: config_1.APPROVAL_ACTIONS_ENABLED,
        approvalActionsDryRun: config_1.APPROVAL_ACTIONS_DRY_RUN,
        distIndexPath: DIST_INDEX_PATH,
        distBuiltAt,
    };
}
function computeSnapshotFreshness(snapshot, monitorIntervalMs, now) {
    const snapshotTime = Date.parse(snapshot.generatedAt);
    const ageMs = Number.isNaN(snapshotTime) ? Number.MAX_SAFE_INTEGER : Math.max(0, now.getTime() - snapshotTime);
    const okThreshold = Math.max(60_000, monitorIntervalMs * 12);
    const warnThreshold = Math.max(5 * 60_000, monitorIntervalMs * 48);
    let status = "ok";
    if (ageMs > warnThreshold) {
        status = "stale";
    }
    else if (ageMs > okThreshold) {
        status = "warn";
    }
    return {
        generatedAt: snapshot.generatedAt,
        ageMs,
        status,
        thresholdsMs: {
            ok: okThreshold,
            warn: warnThreshold,
        },
    };
}
function resolveOverallStatus(snapshotStatus, monitorStatus) {
    if (snapshotStatus === "stale" || monitorStatus === "stale") {
        return "stale";
    }
    if (snapshotStatus === "warn" || monitorStatus === "warn" || monitorStatus === "missing") {
        return "warn";
    }
    return "ok";
}
