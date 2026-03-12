"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.UI_QUICK_FILTERS = exports.UI_PREFERENCES_PATH = void 0;
exports.defaultUiPreferences = defaultUiPreferences;
exports.loadUiPreferences = loadUiPreferences;
exports.saveUiPreferences = saveUiPreferences;
exports.isUiQuickFilter = isUiQuickFilter;
exports.isUiLanguage = isUiLanguage;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
exports.UI_PREFERENCES_PATH = (0, node_path_1.join)(process.cwd(), "runtime", "ui-preferences.json");
exports.UI_QUICK_FILTERS = [
    "all",
    "attention",
    "todo",
    "in_progress",
    "blocked",
    "done",
];
function defaultUiPreferences(now = new Date().toISOString()) {
    return {
        language: "zh",
        compactStatusStrip: true,
        quickFilter: "all",
        taskFilters: {},
        updatedAt: now,
    };
}
async function loadUiPreferences() {
    let parsed;
    let issues = [];
    try {
        const raw = await (0, promises_1.readFile)(exports.UI_PREFERENCES_PATH, "utf8");
        parsed = JSON.parse(raw);
    }
    catch (error) {
        const fallback = defaultUiPreferences();
        const reason = error instanceof Error ? error.message : "unable to read preference file";
        issues = [`preferences fallback applied: ${reason}`];
        await writeUiPreferences(fallback);
        return {
            path: exports.UI_PREFERENCES_PATH,
            preferences: fallback,
            issues,
        };
    }
    const normalized = normalizeUiPreferences(parsed);
    if (normalized.issues.length > 0) {
        await writeUiPreferences(normalized.preferences);
    }
    return {
        path: exports.UI_PREFERENCES_PATH,
        preferences: normalized.preferences,
        issues: normalized.issues,
    };
}
async function saveUiPreferences(preferences) {
    const normalized = normalizeUiPreferences(preferences);
    await writeUiPreferences(normalized.preferences);
    return {
        path: exports.UI_PREFERENCES_PATH,
        preferences: normalized.preferences,
        issues: normalized.issues,
    };
}
function isUiQuickFilter(input) {
    return exports.UI_QUICK_FILTERS.includes(input);
}
function isUiLanguage(input) {
    return input === "en" || input === "zh";
}
function normalizeUiPreferences(input) {
    const now = new Date().toISOString();
    const base = defaultUiPreferences(now);
    const issues = [];
    const obj = asObject(input);
    if (!obj) {
        issues.push("preferences must be a JSON object");
        return { preferences: base, issues };
    }
    let compactStatusStrip = base.compactStatusStrip;
    let language = base.language;
    if (typeof obj.language === "string") {
        const normalizedLanguage = obj.language.trim().toLowerCase();
        if (isUiLanguage(normalizedLanguage)) {
            language = normalizedLanguage;
        }
        else {
            issues.push("language must be one of: en, zh");
        }
    }
    else if (obj.language !== undefined) {
        issues.push("language must be a string");
    }
    if (obj.compactStatusStrip !== undefined) {
        if (typeof obj.compactStatusStrip === "boolean") {
            compactStatusStrip = obj.compactStatusStrip;
        }
        else {
            issues.push("compactStatusStrip must be a boolean");
        }
    }
    let quickFilter = base.quickFilter;
    if (typeof obj.quickFilter === "string") {
        const trimmed = obj.quickFilter.trim();
        if (isUiQuickFilter(trimmed)) {
            quickFilter = trimmed;
        }
        else {
            issues.push("quickFilter must be one of: all, attention, todo, in_progress, blocked, done");
        }
    }
    else if (obj.quickFilter !== undefined) {
        issues.push("quickFilter must be a string");
    }
    const taskFilters = normalizeTaskFilters(obj.taskFilters, issues);
    if (taskFilters.status === undefined && isTaskState(quickFilter)) {
        taskFilters.status = quickFilter;
    }
    let updatedAt = now;
    if (typeof obj.updatedAt === "string" && !Number.isNaN(Date.parse(obj.updatedAt))) {
        updatedAt = new Date(obj.updatedAt).toISOString();
    }
    else if (obj.updatedAt !== undefined) {
        issues.push("updatedAt must be an ISO-8601 timestamp");
    }
    return {
        preferences: {
            language,
            compactStatusStrip,
            quickFilter,
            taskFilters,
            updatedAt,
        },
        issues,
    };
}
function normalizeTaskFilters(input, issues) {
    const out = {};
    if (input === undefined)
        return out;
    const obj = asObject(input);
    if (!obj) {
        issues.push("taskFilters must be an object");
        return out;
    }
    if (typeof obj.status === "string") {
        const status = obj.status.trim();
        if (!status) {
            out.status = undefined;
        }
        else if (isTaskState(status)) {
            out.status = status;
        }
        else {
            issues.push("taskFilters.status must be one of: todo, in_progress, blocked, done");
        }
    }
    else if (obj.status !== undefined) {
        issues.push("taskFilters.status must be a string");
    }
    const owner = normalizeOptionalString(obj.owner, "taskFilters.owner", 80, issues);
    if (owner)
        out.owner = owner;
    const project = normalizeOptionalString(obj.project, "taskFilters.project", 120, issues);
    if (project)
        out.project = project;
    return out;
}
function normalizeOptionalString(input, label, maxLength, issues) {
    if (input === undefined)
        return undefined;
    if (typeof input !== "string") {
        issues.push(`${label} must be a string`);
        return undefined;
    }
    const trimmed = input.trim();
    if (!trimmed)
        return undefined;
    if (/[\u0000-\u001F\u007F]/.test(trimmed)) {
        issues.push(`${label} contains control characters`);
        return undefined;
    }
    if (trimmed.length > maxLength) {
        issues.push(`${label} must be <= ${maxLength} characters`);
        return undefined;
    }
    return trimmed;
}
function isTaskState(input) {
    return input === "todo" || input === "in_progress" || input === "blocked" || input === "done";
}
function asObject(input) {
    return input !== null && typeof input === "object" && !Array.isArray(input)
        ? input
        : undefined;
}
async function writeUiPreferences(preferences) {
    await (0, promises_1.mkdir)((0, node_path_1.join)(process.cwd(), "runtime"), { recursive: true });
    await (0, promises_1.writeFile)(exports.UI_PREFERENCES_PATH, `${JSON.stringify(preferences, null, 2)}\n`, "utf8");
}
