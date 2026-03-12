"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateExportFileDryRun = validateExportFileDryRun;
exports.validateExportBundleDryRun = validateExportBundleDryRun;
exports.resolveExportPath = resolveExportPath;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const export_bundle_1 = require("./export-bundle");
async function validateExportFileDryRun(inputPath) {
    const path = resolveExportPath(inputPath);
    const source = `file:${path}`;
    try {
        const raw = await (0, promises_1.readFile)(path, "utf8");
        const parsed = JSON.parse(raw);
        return validateExportBundleDryRun(parsed, source);
    }
    catch (error) {
        return {
            validatedAt: new Date().toISOString(),
            source,
            valid: false,
            issues: [error instanceof Error ? error.message : "Failed to read export bundle file."],
            warnings: [],
            summary: {
                sessions: 0,
                projects: 0,
                tasks: 0,
                exceptions: 0,
            },
        };
    }
}
function validateExportBundleDryRun(input, source = "payload") {
    const issues = [];
    const warnings = [];
    const validatedAt = new Date().toISOString();
    const root = asObject(input);
    if (!root) {
        return {
            validatedAt,
            source,
            valid: false,
            issues: ["bundle must be a JSON object."],
            warnings: [],
            summary: {
                sessions: 0,
                projects: 0,
                tasks: 0,
                exceptions: 0,
            },
        };
    }
    const schemaVersion = asString(root.schemaVersion);
    if (!schemaVersion) {
        issues.push("schemaVersion is required.");
    }
    else if (schemaVersion !== "phase-9") {
        warnings.push(`schemaVersion '${schemaVersion}' differs from expected 'phase-9'.`);
    }
    requireIsoString(root.exportedAt, "exportedAt", issues);
    requireIsoString(root.snapshotGeneratedAt, "snapshotGeneratedAt", issues);
    const sessions = asArray(root.sessions);
    if (!sessions) {
        issues.push("sessions must be an array.");
    }
    else {
        validateSessions(sessions, issues);
    }
    const projectsRoot = asObject(root.projects);
    if (!projectsRoot) {
        issues.push("projects must be an object.");
    }
    else {
        requireIsoString(projectsRoot.updatedAt, "projects.updatedAt", issues);
        const projects = asArray(projectsRoot.projects);
        if (!projects) {
            issues.push("projects.projects must be an array.");
        }
        else {
            validateProjects(projects, issues);
        }
    }
    const tasksRoot = asObject(root.tasks);
    if (!tasksRoot) {
        issues.push("tasks must be an object.");
    }
    else {
        requireIsoString(tasksRoot.updatedAt, "tasks.updatedAt", issues);
        const tasks = asArray(tasksRoot.tasks);
        if (!tasks) {
            issues.push("tasks.tasks must be an array.");
        }
        else {
            validateTasks(tasks, issues);
        }
    }
    const budgets = asObject(root.budgets);
    if (!budgets) {
        issues.push("budgets must be an object.");
    }
    else {
        if (!asObject(budgets.policy))
            issues.push("budgets.policy must be an object.");
        if (!asObject(budgets.summary))
            issues.push("budgets.summary must be an object.");
        const budgetIssues = asArray(budgets.issues);
        if (budgetIssues && budgetIssues.length > 0) {
            warnings.push(`budgets.issues contains ${budgetIssues.length} warning(s).`);
        }
    }
    const exceptions = asObject(root.exceptions);
    if (!exceptions) {
        issues.push("exceptions must be an object.");
    }
    else if (!asObject(exceptions.counts)) {
        issues.push("exceptions.counts must be an object.");
    }
    const exceptionsFeed = asObject(root.exceptionsFeed);
    if (!exceptionsFeed) {
        issues.push("exceptionsFeed must be an object.");
    }
    else {
        const items = asArray(exceptionsFeed.items);
        if (!items) {
            issues.push("exceptionsFeed.items must be an array.");
        }
        if (!asObject(exceptionsFeed.counts)) {
            issues.push("exceptionsFeed.counts must be an object.");
        }
    }
    if (asBoolean(root.ok) !== true) {
        warnings.push("ok is not true; bundle may be incomplete.");
    }
    const projectCount = asArray(projectsRoot?.projects)?.length ?? 0;
    const taskCount = asArray(tasksRoot?.tasks)?.length ?? 0;
    const sessionCount = sessions?.length ?? 0;
    const exceptionCount = asArray(exceptionsFeed?.items)?.length ?? 0;
    return {
        validatedAt,
        source,
        valid: issues.length === 0,
        issues,
        warnings,
        summary: {
            sessions: sessionCount,
            projects: projectCount,
            tasks: taskCount,
            exceptions: exceptionCount,
        },
    };
}
function validateSessions(items, issues) {
    const seen = new Set();
    items.forEach((item, index) => {
        const obj = asObject(item);
        if (!obj) {
            issues.push(`sessions[${index}] must be an object.`);
            return;
        }
        const key = asString(obj.sessionKey)?.trim();
        const state = asString(obj.state)?.trim();
        if (!key)
            issues.push(`sessions[${index}].sessionKey is required.`);
        if (!state)
            issues.push(`sessions[${index}].state is required.`);
        if (key && seen.has(key))
            issues.push(`sessions contains duplicate sessionKey '${key}'.`);
        if (key)
            seen.add(key);
    });
}
function validateProjects(items, issues) {
    const seen = new Set();
    items.forEach((item, index) => {
        const obj = asObject(item);
        if (!obj) {
            issues.push(`projects.projects[${index}] must be an object.`);
            return;
        }
        const id = asString(obj.projectId)?.trim();
        if (!id)
            issues.push(`projects.projects[${index}].projectId is required.`);
        if (id && seen.has(id))
            issues.push(`projects.projects has duplicate projectId '${id}'.`);
        if (id)
            seen.add(id);
    });
}
function validateTasks(items, issues) {
    const seen = new Set();
    items.forEach((item, index) => {
        const obj = asObject(item);
        if (!obj) {
            issues.push(`tasks.tasks[${index}] must be an object.`);
            return;
        }
        const taskId = asString(obj.taskId)?.trim();
        const projectId = asString(obj.projectId)?.trim();
        if (!taskId)
            issues.push(`tasks.tasks[${index}].taskId is required.`);
        if (!projectId)
            issues.push(`tasks.tasks[${index}].projectId is required.`);
        const composite = taskId && projectId ? `${projectId}:${taskId}` : "";
        if (composite && seen.has(composite))
            issues.push(`tasks.tasks has duplicate key '${composite}'.`);
        if (composite)
            seen.add(composite);
    });
}
function requireIsoString(input, label, issues) {
    const value = asString(input);
    if (!value) {
        issues.push(`${label} is required.`);
        return;
    }
    if (Number.isNaN(Date.parse(value))) {
        issues.push(`${label} must be an ISO date-time string.`);
    }
}
function resolveExportPath(inputPath) {
    const trimmed = inputPath.trim();
    if (!trimmed) {
        throw new Error("Export path is required.");
    }
    const normalized = (0, node_path_1.normalize)(trimmed).replaceAll("\\", "/");
    const looksLikeWorkspaceRuntimePath = normalized === "runtime/exports" ||
        normalized.startsWith("runtime/exports/") ||
        normalized.startsWith("./runtime/exports/");
    const candidate = (0, node_path_1.isAbsolute)(trimmed)
        ? (0, node_path_1.resolve)(trimmed)
        : looksLikeWorkspaceRuntimePath
            ? (0, node_path_1.resolve)(trimmed)
            : (0, node_path_1.resolve)((0, node_path_1.join)(export_bundle_1.EXPORTS_DIR, normalized));
    const allowedRoot = (0, node_path_1.resolve)(export_bundle_1.EXPORTS_DIR);
    if (!candidate.startsWith(allowedRoot)) {
        throw new Error(`Path is outside runtime exports directory: ${candidate}`);
    }
    if (!candidate.endsWith(".json")) {
        throw new Error("Export file must be a .json file.");
    }
    return candidate;
}
function asString(input) {
    return typeof input === "string" ? input : undefined;
}
function asBoolean(input) {
    return typeof input === "boolean" ? input : undefined;
}
function asObject(input) {
    return input !== null && typeof input === "object" && !Array.isArray(input)
        ? input
        : undefined;
}
function asArray(input) {
    return Array.isArray(input) ? input : undefined;
}
