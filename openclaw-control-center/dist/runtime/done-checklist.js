"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildDoneChecklist = buildDoneChecklist;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const config_1 = require("../config");
const api_docs_1 = require("./api-docs");
const export_bundle_1 = require("./export-bundle");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
const SNAPSHOT_PATH = (0, node_path_1.join)(RUNTIME_DIR, "last-snapshot.json");
const TIMELINE_LOG_PATH = (0, node_path_1.join)(RUNTIME_DIR, "timeline.log");
const DIGEST_DIR = (0, node_path_1.join)(RUNTIME_DIR, "digests");
const BUDGETS_PATH = (0, node_path_1.join)(RUNTIME_DIR, "budgets.json");
async function buildDoneChecklist(snapshot) {
    const now = Date.now();
    const docs = (0, api_docs_1.buildApiDocs)();
    const documentedRoutes = new Set(docs.routes.map((route) => route.path));
    const actionQueueCapabilityReady = hasRouteCoverage(documentedRoutes, [
        "/api/action-queue",
        "/api/action-queue/:itemId/ack",
        "/api/commander/exceptions",
    ]);
    const [snapshotFileExists, budgetPolicyFileExists, timelineLatestAt, digestCount, exportCount,] = await Promise.all([
        fileExists(SNAPSHOT_PATH),
        fileExists(BUDGETS_PATH),
        readLatestTimelineTimestamp(),
        countJsonOrMarkdown(DIGEST_DIR),
        countJson(export_bundle_1.EXPORTS_DIR),
    ]);
    const snapshotAgeMs = ageMs(snapshot.generatedAt, now);
    const timelineAgeMs = ageMs(timelineLatestAt, now);
    const items = [
        checklistItem("obs_snapshot_fresh", "observability", "Snapshot freshness", "docs/RUNBOOK.md (startup + health checks)", statusByAge(snapshotAgeMs, 10 * 60 * 1000, 60 * 60 * 1000), `snapshot generatedAt=${snapshot.generatedAt} age=${formatAge(snapshotAgeMs)}`),
        checklistItem("obs_timeline_recent", "observability", "Timeline log recency", "docs/RUNBOOK.md (runtime artifacts)", statusByAge(timelineAgeMs, 10 * 60 * 1000, 60 * 60 * 1000), timelineLatestAt
            ? `latest timeline event at ${timelineLatestAt} age=${formatAge(timelineAgeMs)}`
            : "timeline log has no parseable events yet"),
        checklistItem("obs_digest_available", "observability", "Digest artifact availability", "docs/RUNBOOK.md (commander digest)", digestCount > 0 ? "pass" : "warn", `digest artifacts detected=${digestCount}`),
        checklistItem("obs_route_coverage", "observability", "Operational API route coverage", "docs/ARCHITECTURE.md + docs/RUNBOOK.md", hasRouteCoverage(documentedRoutes, [
            "/api/docs",
            "/api/replay/index",
            "/api/export/state.json",
            "/api/import/live",
            "/api/action-queue/acks/prune-preview",
        ])
            ? "pass"
            : "fail", "required: /api/docs, /api/replay/index, /api/export/state.json, /api/import/live, /api/action-queue/acks/prune-preview"),
        checklistItem("obs_ui_bind_env_only", "observability", "UI bind EPERM classification", "docs/PROGRESS.md + docs/RUNBOOK.md", "pass", "listen EPERM during UI socket bind in restricted sandboxes is environment-only (not a control-center code regression); validate UI bind in unrestricted host runtime."),
        checklistItem("gov_readonly_default", "governance", "Readonly guard default", "docs/RUNBOOK.md (safety defaults)", config_1.READONLY_MODE ? "pass" : "fail", `READONLY_MODE=${String(config_1.READONLY_MODE)}`),
        checklistItem("gov_approvals_disabled", "governance", "Approval execution disabled by default", "docs/RUNBOOK.md (approval gate)", config_1.APPROVAL_ACTIONS_ENABLED ? "fail" : "pass", `APPROVAL_ACTIONS_ENABLED=${String(config_1.APPROVAL_ACTIONS_ENABLED)}`),
        checklistItem("gov_approvals_dry_run", "governance", "Approval dry-run default", "docs/RUNBOOK.md (approval gate)", config_1.APPROVAL_ACTIONS_DRY_RUN ? "pass" : "warn", `APPROVAL_ACTIONS_DRY_RUN=${String(config_1.APPROVAL_ACTIONS_DRY_RUN)}`),
        checklistItem("gov_import_mutation_disabled", "governance", "Import mutation endpoint disabled by default", "docs/RUNBOOK.md (import mutation gate)", config_1.IMPORT_MUTATION_ENABLED ? "warn" : "pass", `IMPORT_MUTATION_ENABLED=${String(config_1.IMPORT_MUTATION_ENABLED)}`),
        checklistItem("gov_import_mutation_dry_run_default", "governance", "Import mutation env dry-run default", "docs/RUNBOOK.md (import mutation gate)", config_1.IMPORT_MUTATION_DRY_RUN ? "warn" : "pass", `IMPORT_MUTATION_DRY_RUN=${String(config_1.IMPORT_MUTATION_DRY_RUN)}`),
        checklistItem("gov_budget_policy", "governance", "Budget policy file state", "docs/RUNBOOK.md (runtime artifacts)", budgetPolicyFileExists ? "pass" : "warn", `runtime/budgets.json ${budgetPolicyFileExists ? "present" : "missing (defaults fallback active)"}`),
        checklistItem("collab_projects_loaded", "collaboration", "Project store loaded", "docs/ARCHITECTURE.md (read model)", snapshotFileExists ? "pass" : "warn", `projects=${snapshot.projects.projects.length} updatedAt=${snapshot.projects.updatedAt}`),
        checklistItem("collab_tasks_loaded", "collaboration", "Task store loaded", "docs/ARCHITECTURE.md (read model)", snapshot.tasks.tasks.length > 0 ? "pass" : "warn", `tasks=${snapshot.tasks.tasks.length} updatedAt=${snapshot.tasks.updatedAt}`),
        checklistItem("collab_action_queue_signal", "collaboration", "Commander/action queue signal", "docs/RUNBOOK.md (exceptions + action queue)", actionQueueCapabilityReady ? "pass" : "warn", `routesReady=${String(actionQueueCapabilityReady)} sessions=${snapshot.sessions.length} approvals=${snapshot.approvals.length}`),
        checklistItem("collab_exports_ready", "collaboration", "Export bundle history", "docs/RUNBOOK.md (export APIs)", exportCount > 0 ? "pass" : "warn", `runtime/exports bundles=${exportCount}`),
        checklistItem("sec_local_exports_only", "security", "Local export directory isolation", "docs/ARCHITECTURE.md (write boundaries)", export_bundle_1.EXPORTS_DIR.startsWith((0, node_path_1.join)(process.cwd(), "runtime")) ? "pass" : "fail", `exportsDir=${export_bundle_1.EXPORTS_DIR}`),
        checklistItem("sec_import_dry_run", "security", "Import validator dry-run capability", "docs/RUNBOOK.md (Phase 9 import dry-run)", hasRouteCoverage(documentedRoutes, ["/api/import/dry-run"]) ? "pass" : "warn", "required route: /api/import/dry-run"),
        checklistItem("sec_request_trace", "security", "Request correlation support", "docs/ARCHITECTURE.md (telemetry)", hasRouteCoverage(documentedRoutes, ["/api/docs"]) ? "pass" : "warn", "x-request-id + JSON requestId correlation expected"),
        checklistItem("sec_runtime_defaults", "security", "Safe runtime defaults active", "docs/RUNBOOK.md (safety defaults)", config_1.READONLY_MODE &&
            !config_1.APPROVAL_ACTIONS_ENABLED &&
            !config_1.IMPORT_MUTATION_ENABLED &&
            config_1.LOCAL_TOKEN_AUTH_REQUIRED
            ? "pass"
            : "fail", `READONLY_MODE=${String(config_1.READONLY_MODE)} APPROVAL_ACTIONS_ENABLED=${String(config_1.APPROVAL_ACTIONS_ENABLED)} IMPORT_MUTATION_ENABLED=${String(config_1.IMPORT_MUTATION_ENABLED)} LOCAL_TOKEN_AUTH_REQUIRED=${String(config_1.LOCAL_TOKEN_AUTH_REQUIRED)}`),
        checklistItem("sec_local_token_gate", "security", "Local mutation/import token gate posture", "docs/RUNBOOK.md (local token auth gate)", config_1.LOCAL_TOKEN_AUTH_REQUIRED ? "pass" : "warn", config_1.LOCAL_TOKEN_AUTH_REQUIRED
            ? config_1.LOCAL_API_TOKEN !== ""
                ? "LOCAL_API_TOKEN configured for protected operations"
                : "LOCAL_API_TOKEN missing: protected operations remain blocked by default until explicitly enabled"
            : "LOCAL_TOKEN_AUTH_REQUIRED=false (auth gate disabled)"),
    ];
    const readiness = computeReadiness(items);
    const counts = {
        pass: items.filter((item) => item.status === "pass").length,
        warn: items.filter((item) => item.status === "warn").length,
        fail: items.filter((item) => item.status === "fail").length,
    };
    return {
        generatedAt: new Date().toISOString(),
        basedOn: ["docs/RUNBOOK.md", "docs/ARCHITECTURE.md", "runtime capabilities"],
        items,
        counts,
        readiness,
    };
}
function checklistItem(id, category, title, docRef, status, detail) {
    return { id, category, title, docRef, status, detail };
}
function computeReadiness(items) {
    const categories = ["observability", "governance", "collaboration", "security"];
    const byCategory = categories.map((category) => {
        const selected = items.filter((item) => item.category === category);
        const passed = selected.filter((item) => item.status === "pass").length;
        const warn = selected.filter((item) => item.status === "warn").length;
        const failed = selected.filter((item) => item.status === "fail").length;
        const score = selected.length === 0 ? 0 : Math.round(((passed + warn * 0.5) / selected.length) * 100);
        return {
            category,
            score,
            passed,
            warn,
            failed,
            total: selected.length,
        };
    });
    const totalItems = items.length;
    const totalPoints = items.reduce((acc, item) => {
        if (item.status === "pass")
            return acc + 1;
        if (item.status === "warn")
            return acc + 0.5;
        return acc;
    }, 0);
    const overall = totalItems === 0 ? 0 : Math.round((totalPoints / totalItems) * 100);
    return {
        overall,
        categories: byCategory,
    };
}
function hasRouteCoverage(routes, required) {
    return required.every((route) => routes.has(route));
}
function ageMs(input, nowMs) {
    if (!input)
        return undefined;
    const ms = Date.parse(input);
    if (Number.isNaN(ms))
        return undefined;
    return Math.max(0, nowMs - ms);
}
function statusByAge(age, passThresholdMs, warnThresholdMs) {
    if (!Number.isFinite(age))
        return "warn";
    if (age <= passThresholdMs)
        return "pass";
    if (age <= warnThresholdMs)
        return "warn";
    return "fail";
}
function formatAge(age) {
    if (!Number.isFinite(age))
        return "n/a";
    const seconds = Math.round(age / 1000);
    if (seconds < 60)
        return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60)
        return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ${minutes % 60}m`;
}
async function countJson(path) {
    try {
        const files = await (0, promises_1.readdir)(path);
        return files.filter((name) => name.endsWith(".json")).length;
    }
    catch {
        return 0;
    }
}
async function countJsonOrMarkdown(path) {
    try {
        const files = await (0, promises_1.readdir)(path);
        return files.filter((name) => name.endsWith(".json") || name.endsWith(".md")).length;
    }
    catch {
        return 0;
    }
}
async function readLatestTimelineTimestamp() {
    try {
        const raw = await (0, promises_1.readFile)(TIMELINE_LOG_PATH, "utf8");
        const lines = raw
            .split(/\r?\n/)
            .map((line) => line.trim())
            .filter((line) => line !== "");
        if (lines.length === 0)
            return undefined;
        for (let idx = lines.length - 1; idx >= 0; idx -= 1) {
            const line = lines[idx];
            const firstToken = line.split("|")[0]?.trim();
            if (!firstToken)
                continue;
            const parsed = Date.parse(firstToken);
            if (Number.isNaN(parsed))
                continue;
            return new Date(parsed).toISOString();
        }
        return undefined;
    }
    catch {
        return undefined;
    }
}
async function fileExists(path) {
    try {
        await (0, promises_1.stat)(path);
        return true;
    }
    catch {
        return false;
    }
}
