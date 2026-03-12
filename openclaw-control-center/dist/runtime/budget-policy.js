"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEFAULT_BUDGET_POLICY = exports.BUDGET_POLICY_PATH = void 0;
exports.loadBudgetPolicy = loadBudgetPolicy;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
exports.BUDGET_POLICY_PATH = (0, node_path_1.join)(RUNTIME_DIR, "budgets.json");
const DEFAULT_WARN_RATIO = 0.8;
exports.DEFAULT_BUDGET_POLICY = {
    defaults: {
        warnRatio: DEFAULT_WARN_RATIO,
    },
    agent: {},
    project: {},
    task: {},
};
async function loadBudgetPolicy() {
    try {
        const raw = await (0, promises_1.readFile)(exports.BUDGET_POLICY_PATH, "utf8");
        const parsed = JSON.parse(raw);
        const issues = [];
        const policy = normalizePolicy(parsed, issues);
        return {
            policy,
            path: exports.BUDGET_POLICY_PATH,
            loadedFromFile: true,
            issues,
        };
    }
    catch (error) {
        const issues = [];
        if (!isErrorWithCode(error, "ENOENT")) {
            issues.push(`failed to load budgets policy: ${error instanceof Error ? error.message : "unknown error"}`);
        }
        return {
            policy: clonePolicy(exports.DEFAULT_BUDGET_POLICY),
            path: exports.BUDGET_POLICY_PATH,
            loadedFromFile: false,
            issues,
        };
    }
}
function normalizePolicy(input, issues) {
    const obj = asObject(input);
    if (!obj) {
        issues.push("budgets policy must be a JSON object");
        return clonePolicy(exports.DEFAULT_BUDGET_POLICY);
    }
    return {
        defaults: normalizeThresholds(obj.defaults, "defaults", issues, true),
        agent: normalizeScopeRecord(obj.agent, "agent", issues),
        project: normalizeScopeRecord(obj.project, "project", issues),
        task: normalizeScopeRecord(obj.task, "task", issues),
    };
}
function normalizeScopeRecord(input, label, issues) {
    const obj = asObject(input);
    if (!obj) {
        if (input !== undefined)
            issues.push(`${label} must be an object`);
        return {};
    }
    const out = {};
    for (const [scopeId, thresholds] of Object.entries(obj)) {
        if (!scopeId.trim()) {
            issues.push(`${label} contains empty key`);
            continue;
        }
        out[scopeId] = normalizeThresholds(thresholds, `${label}.${scopeId}`, issues, false);
    }
    return out;
}
function normalizeThresholds(input, label, issues, includeDefaultWarnRatio) {
    const obj = asObject(input);
    if (!obj) {
        if (input !== undefined)
            issues.push(`${label} must be an object`);
        return includeDefaultWarnRatio ? { warnRatio: DEFAULT_WARN_RATIO } : {};
    }
    const tokensIn = readPositiveNumber(obj.tokensIn, `${label}.tokensIn`, issues);
    const tokensOut = readPositiveNumber(obj.tokensOut, `${label}.tokensOut`, issues);
    const totalTokens = readPositiveNumber(obj.totalTokens, `${label}.totalTokens`, issues);
    const cost = readPositiveNumber(obj.cost, `${label}.cost`, issues);
    const warnRatio = readWarnRatio(obj.warnRatio, `${label}.warnRatio`, issues);
    return {
        ...(tokensIn !== undefined ? { tokensIn } : {}),
        ...(tokensOut !== undefined ? { tokensOut } : {}),
        ...(totalTokens !== undefined ? { totalTokens } : {}),
        ...(cost !== undefined ? { cost } : {}),
        ...(warnRatio !== undefined
            ? { warnRatio }
            : includeDefaultWarnRatio
                ? { warnRatio: DEFAULT_WARN_RATIO }
                : {}),
    };
}
function readPositiveNumber(input, label, issues) {
    if (input === undefined)
        return undefined;
    if (typeof input !== "number" || !Number.isFinite(input) || input <= 0) {
        issues.push(`${label} must be a finite number > 0`);
        return undefined;
    }
    return input;
}
function readWarnRatio(input, label, issues) {
    if (input === undefined)
        return undefined;
    if (typeof input !== "number" || !Number.isFinite(input) || input <= 0 || input >= 1) {
        issues.push(`${label} must be a finite number > 0 and < 1`);
        return undefined;
    }
    return input;
}
function clonePolicy(policy) {
    return {
        defaults: { ...policy.defaults },
        agent: { ...policy.agent },
        project: { ...policy.project },
        task: { ...policy.task },
    };
}
function asObject(v) {
    return v !== null && typeof v === "object" && !Array.isArray(v) ? v : undefined;
}
function isErrorWithCode(error, code) {
    return error !== null && typeof error === "object" && "code" in error && error.code === code;
}
