"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OPERATION_AUDIT_LOG_PATH = void 0;
exports.appendOperationAudit = appendOperationAudit;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
exports.OPERATION_AUDIT_LOG_PATH = (0, node_path_1.join)(RUNTIME_DIR, "operation-audit.log");
async function appendOperationAudit(input) {
    const entry = {
        ...input,
        timestamp: new Date().toISOString(),
    };
    await (0, promises_1.mkdir)(RUNTIME_DIR, { recursive: true });
    await (0, promises_1.appendFile)(exports.OPERATION_AUDIT_LOG_PATH, `${JSON.stringify(entry)}\n`, "utf8");
    return entry;
}
