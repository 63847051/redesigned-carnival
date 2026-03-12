"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadAuditTimeline = loadAuditTimeline;
exports.filterAuditTimeline = filterAuditTimeline;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const commander_1 = require("./commander");
const operation_audit_1 = require("./operation-audit");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
const TIMELINE_LOG_PATH = (0, node_path_1.join)(RUNTIME_DIR, "timeline.log");
const APPROVAL_ACTIONS_LOG_PATH = (0, node_path_1.join)(RUNTIME_DIR, "approval-actions.log");
async function loadAuditTimeline(snapshot) {
    const [monitorEvents, approvalEvents, operationEvents] = await Promise.all([
        loadMonitorEvents(),
        loadApprovalActionEvents(),
        loadOperationEvents(),
    ]);
    const events = [snapshotEvent(snapshot), ...monitorEvents, ...approvalEvents, ...operationEvents].sort(compareTimelineEvents);
    return {
        generatedAt: new Date().toISOString(),
        events,
        counts: {
            info: events.filter((item) => item.severity === "info").length,
            warn: events.filter((item) => item.severity === "warn").length,
            "action-required": events.filter((item) => item.severity === "action-required").length,
            error: events.filter((item) => item.severity === "error").length,
        },
    };
}
function filterAuditTimeline(timeline, severity) {
    if (severity === "all")
        return timeline;
    const events = timeline.events.filter((event) => event.severity === severity);
    return {
        generatedAt: timeline.generatedAt,
        events,
        counts: {
            info: events.filter((item) => item.severity === "info").length,
            warn: events.filter((item) => item.severity === "warn").length,
            "action-required": events.filter((item) => item.severity === "action-required").length,
            error: events.filter((item) => item.severity === "error").length,
        },
    };
}
function snapshotEvent(snapshot) {
    const exceptions = (0, commander_1.commanderExceptions)(snapshot);
    const severity = deriveSnapshotSeverity(exceptions.counts);
    return {
        timestamp: snapshot.generatedAt,
        severity,
        source: "snapshot",
        message: `snapshot sessions=${snapshot.sessions.length} approvals=${snapshot.approvals.length} ` +
            `blocked=${exceptions.counts.blocked} errors=${exceptions.counts.errors} ` +
            `pendingApprovals=${exceptions.counts.pendingApprovals} overBudget=${exceptions.counts.overBudget} tasksDue=${exceptions.counts.tasksDue}`,
    };
}
async function loadMonitorEvents() {
    const raw = await safeReadFile(TIMELINE_LOG_PATH);
    if (!raw)
        return [];
    const events = [];
    const lines = raw.split(/\r?\n/).filter((line) => line.trim() !== "");
    for (const line of lines) {
        const parsed = parseMonitorLine(line);
        if (parsed)
            events.push(parsed);
    }
    return events;
}
async function loadApprovalActionEvents() {
    const raw = await safeReadFile(APPROVAL_ACTIONS_LOG_PATH);
    if (!raw)
        return [];
    const events = [];
    const lines = raw.split(/\r?\n/).filter((line) => line.trim() !== "");
    for (const line of lines) {
        const parsed = parseApprovalLine(line);
        if (parsed)
            events.push(parsed);
    }
    return events;
}
async function loadOperationEvents() {
    const raw = await safeReadFile(operation_audit_1.OPERATION_AUDIT_LOG_PATH);
    if (!raw)
        return [];
    const events = [];
    const lines = raw.split(/\r?\n/).filter((line) => line.trim() !== "");
    for (const line of lines) {
        const parsed = parseOperationLine(line);
        if (parsed)
            events.push(parsed);
    }
    return events;
}
function parseMonitorLine(line) {
    const match = line.match(/^(\S+)\s+\|\s+(.*)$/);
    if (!match)
        return null;
    const timestamp = toIso(match[1]);
    if (!timestamp)
        return null;
    const details = match[2].trim();
    const alertsMatch = details.match(/alerts=(\d+)/);
    const alerts = alertsMatch ? Number.parseInt(alertsMatch[1], 10) : 0;
    return {
        timestamp,
        severity: alerts > 0 ? "warn" : "info",
        source: "monitor",
        message: details,
    };
}
function parseApprovalLine(line) {
    try {
        const obj = JSON.parse(line);
        const timestamp = typeof obj.timestamp === "string" && !Number.isNaN(Date.parse(obj.timestamp))
            ? new Date(obj.timestamp).toISOString()
            : new Date().toISOString();
        const action = asString(obj.action) ?? "approval-action";
        const approvalId = asString(obj.approvalId) ?? "unknown";
        const message = asString(obj.message) ?? "approval action event";
        const mode = asString(obj.mode) ?? "unknown";
        const ok = obj.ok === true;
        return {
            timestamp,
            severity: deriveApprovalSeverity(ok, mode),
            source: "approval-action",
            message: `${action} ${approvalId} (${mode}) ${message}`,
        };
    }
    catch {
        return null;
    }
}
function parseOperationLine(line) {
    try {
        const obj = JSON.parse(line);
        const timestamp = typeof obj.timestamp === "string" && !Number.isNaN(Date.parse(obj.timestamp))
            ? new Date(obj.timestamp).toISOString()
            : new Date().toISOString();
        const action = asString(obj.action) ?? "operation";
        const source = asString(obj.source) ?? "unknown";
        const detail = asString(obj.detail) ?? "operation audit";
        const ok = obj.ok === true;
        return {
            timestamp,
            severity: deriveOperationSeverity(action, ok, detail),
            source: "operation",
            message: `${action} (${source}) ${detail}`,
        };
    }
    catch {
        return null;
    }
}
function deriveSnapshotSeverity(counts) {
    if (counts.errors > 0)
        return "error";
    if (counts.pendingApprovals > 0 || counts.overBudget > 0)
        return "action-required";
    if (counts.blocked > 0 || counts.tasksDue > 0)
        return "warn";
    return "info";
}
function deriveApprovalSeverity(ok, mode) {
    if (!ok && mode === "live")
        return "error";
    if (mode === "blocked")
        return "warn";
    if (!ok)
        return "warn";
    if (mode === "live")
        return "action-required";
    return "info";
}
function deriveOperationSeverity(action, ok, detail) {
    if (action === "backup_export") {
        return ok ? "info" : "error";
    }
    if (action === "import_dry_run") {
        return ok ? "info" : "warn";
    }
    if (action === "import_apply") {
        return ok ? "action-required" : "error";
    }
    if (action === "ack_prune") {
        return ok ? "info" : "warn";
    }
    if (action === "task_heartbeat") {
        if (!ok)
            return "warn";
        return detail.startsWith("live ") ? "action-required" : "info";
    }
    return ok ? "info" : "warn";
}
async function safeReadFile(path) {
    try {
        return await (0, promises_1.readFile)(path, "utf8");
    }
    catch {
        return "";
    }
}
function toMs(value) {
    const ms = Date.parse(value);
    return Number.isNaN(ms) ? 0 : ms;
}
function toIso(value) {
    const ms = Date.parse(value);
    if (Number.isNaN(ms))
        return undefined;
    return new Date(ms).toISOString();
}
function compareTimelineEvents(a, b) {
    const timeDiff = toMs(b.timestamp) - toMs(a.timestamp);
    if (timeDiff !== 0)
        return timeDiff;
    const severityDiff = severityRank(a.severity) - severityRank(b.severity);
    if (severityDiff !== 0)
        return severityDiff;
    const sourceDiff = a.source.localeCompare(b.source);
    if (sourceDiff !== 0)
        return sourceDiff;
    return a.message.localeCompare(b.message);
}
function severityRank(severity) {
    if (severity === "error")
        return 0;
    if (severity === "action-required")
        return 1;
    if (severity === "warn")
        return 2;
    return 3;
}
function asString(input) {
    return typeof input === "string" ? input : undefined;
}
