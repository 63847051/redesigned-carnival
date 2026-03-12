"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EXPORTS_DIR = void 0;
exports.buildExportBundle = buildExportBundle;
exports.writeExportBundle = writeExportBundle;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const budget_policy_1 = require("./budget-policy");
const commander_1 = require("./commander");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
exports.EXPORTS_DIR = (0, node_path_1.join)(RUNTIME_DIR, "exports");
async function buildExportBundle(snapshot, source, requestId) {
    const budgetPolicy = await (0, budget_policy_1.loadBudgetPolicy)();
    return {
        ok: true,
        schemaVersion: "phase-9",
        source,
        requestId,
        exportedAt: new Date().toISOString(),
        snapshotGeneratedAt: snapshot.generatedAt,
        sessions: snapshot.sessions,
        projects: snapshot.projects,
        tasks: snapshot.tasks,
        budgets: {
            policy: budgetPolicy.policy,
            issues: budgetPolicy.issues,
            summary: snapshot.budgetSummary,
        },
        exceptions: (0, commander_1.commanderExceptions)(snapshot),
        exceptionsFeed: (0, commander_1.commanderExceptionsFeed)(snapshot),
    };
}
async function writeExportBundle(bundle, label) {
    await (0, promises_1.mkdir)(exports.EXPORTS_DIR, { recursive: true });
    const stamp = compactIsoStamp(bundle.exportedAt);
    const safeLabel = sanitizeSegment(label, "export");
    const safeRequest = sanitizeSegment(bundle.requestId, "req");
    const fileName = `${stamp}-${safeLabel}-${safeRequest}.json`;
    const path = (0, node_path_1.join)(exports.EXPORTS_DIR, fileName);
    const body = `${JSON.stringify(bundle, null, 2)}\n`;
    await (0, promises_1.writeFile)(path, body, "utf8");
    return {
        fileName,
        path,
        sizeBytes: Buffer.byteLength(body, "utf8"),
    };
}
function sanitizeSegment(input, fallback) {
    if (!input)
        return fallback;
    const sanitized = input.replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 40);
    return sanitized || fallback;
}
function compactIsoStamp(iso) {
    const parsed = Date.parse(iso);
    const value = Number.isNaN(parsed) ? new Date() : new Date(parsed);
    return value.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z").replace("T", "-");
}
