"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.POLLING_INTERVALS_MS = exports.TASK_HEARTBEAT_MAX_TASKS_PER_RUN = exports.TASK_HEARTBEAT_DRY_RUN = exports.TASK_HEARTBEAT_ENABLED = exports.LOCAL_TOKEN_HEADER = exports.LOCAL_API_TOKEN = exports.LOCAL_TOKEN_AUTH_REQUIRED = exports.IMPORT_MUTATION_DRY_RUN = exports.IMPORT_MUTATION_ENABLED = exports.APPROVAL_ACTIONS_DRY_RUN = exports.APPROVAL_ACTIONS_ENABLED = exports.READONLY_MODE = exports.GATEWAY_URL = void 0;
exports.GATEWAY_URL = readStringEnv(process.env.GATEWAY_URL, "ws://127.0.0.1:18789");
exports.READONLY_MODE = process.env.READONLY_MODE !== "false";
exports.APPROVAL_ACTIONS_ENABLED = process.env.APPROVAL_ACTIONS_ENABLED === "true";
exports.APPROVAL_ACTIONS_DRY_RUN = process.env.APPROVAL_ACTIONS_DRY_RUN !== "false";
exports.IMPORT_MUTATION_ENABLED = process.env.IMPORT_MUTATION_ENABLED === "true";
exports.IMPORT_MUTATION_DRY_RUN = process.env.IMPORT_MUTATION_DRY_RUN === "true";
exports.LOCAL_TOKEN_AUTH_REQUIRED = process.env.LOCAL_TOKEN_AUTH_REQUIRED !== "false";
exports.LOCAL_API_TOKEN = (process.env.LOCAL_API_TOKEN ?? "").trim();
exports.LOCAL_TOKEN_HEADER = "x-local-token";
exports.TASK_HEARTBEAT_ENABLED = process.env.TASK_HEARTBEAT_ENABLED !== "false";
exports.TASK_HEARTBEAT_DRY_RUN = process.env.TASK_HEARTBEAT_DRY_RUN !== "false";
exports.TASK_HEARTBEAT_MAX_TASKS_PER_RUN = parsePositiveInt(process.env.TASK_HEARTBEAT_MAX_TASKS_PER_RUN, 3);
exports.POLLING_INTERVALS_MS = {
    sessionsList: 5000,
    sessionStatus: 2000,
    cron: 10000,
    approvals: 2000,
    canvas: 5000,
};
function parsePositiveInt(input, fallback) {
    const parsed = Number.parseInt(input ?? "", 10);
    if (!Number.isFinite(parsed) || parsed <= 0)
        return fallback;
    return parsed;
}
function readStringEnv(input, fallback) {
    const value = (input ?? "").trim();
    return value === "" ? fallback : value;
}
