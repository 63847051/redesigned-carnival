"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApprovalActionService = exports.APPROVAL_ACTION_AUDIT_LOG_PATH = void 0;
exports.runtimeApprovalGate = runtimeApprovalGate;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const config_1 = require("../config");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
exports.APPROVAL_ACTION_AUDIT_LOG_PATH = (0, node_path_1.join)(RUNTIME_DIR, "approval-actions.log");
class ApprovalActionService {
    client;
    gate;
    constructor(client, gate = runtimeApprovalGate()) {
        this.client = client;
        this.gate = gate;
    }
    async execute(input) {
        const approvalId = input.approvalId.trim();
        const reason = input.reason?.trim();
        const timestamp = new Date().toISOString();
        if (!approvalId) {
            return this.audit({
                ok: false,
                executed: false,
                mode: "blocked",
                action: input.action,
                approvalId: input.approvalId,
                reason,
                message: "approvalId is required.",
                gate: this.gate,
                auditLogPath: exports.APPROVAL_ACTION_AUDIT_LOG_PATH,
                timestamp,
            });
        }
        if (input.action === "reject" && !reason) {
            return this.audit({
                ok: false,
                executed: false,
                mode: "blocked",
                action: input.action,
                approvalId,
                message: "reason is required for reject action.",
                gate: this.gate,
                auditLogPath: exports.APPROVAL_ACTION_AUDIT_LOG_PATH,
                timestamp,
            });
        }
        if (!this.gate.actionsEnabled) {
            return this.audit({
                ok: false,
                executed: false,
                mode: "blocked",
                action: input.action,
                approvalId,
                reason,
                message: "Approval actions are disabled by runtime gate. Set APPROVAL_ACTIONS_ENABLED=true to allow execution.",
                gate: this.gate,
                auditLogPath: exports.APPROVAL_ACTION_AUDIT_LOG_PATH,
                timestamp,
            });
        }
        if (this.gate.dryRun) {
            return this.audit({
                ok: true,
                executed: false,
                mode: "dry_run",
                action: input.action,
                approvalId,
                reason,
                message: "Dry-run mode active. No approve/reject command executed.",
                gate: this.gate,
                auditLogPath: exports.APPROVAL_ACTION_AUDIT_LOG_PATH,
                timestamp,
            });
        }
        if (this.gate.readonlyMode) {
            return this.audit({
                ok: false,
                executed: false,
                mode: "blocked",
                action: input.action,
                approvalId,
                reason,
                message: "Readonly mode blocks approval actions. Set READONLY_MODE=false for live execution.",
                gate: this.gate,
                auditLogPath: exports.APPROVAL_ACTION_AUDIT_LOG_PATH,
                timestamp,
            });
        }
        try {
            const response = await this.invokeClient(input.action, { approvalId, reason });
            return this.audit({
                ok: response.ok,
                executed: true,
                mode: "live",
                action: input.action,
                approvalId,
                reason,
                message: response.ok ? "Approval action executed." : "Approval action response indicated failure.",
                gate: this.gate,
                rawText: response.rawText,
                auditLogPath: exports.APPROVAL_ACTION_AUDIT_LOG_PATH,
                timestamp,
            });
        }
        catch (error) {
            return this.audit({
                ok: false,
                executed: true,
                mode: "live",
                action: input.action,
                approvalId,
                reason,
                message: error instanceof Error ? error.message : "Unknown approval action error.",
                gate: this.gate,
                auditLogPath: exports.APPROVAL_ACTION_AUDIT_LOG_PATH,
                timestamp,
            });
        }
    }
    async invokeClient(action, payload) {
        if (action === "approve") {
            return this.client.approvalsApprove({
                approvalId: payload.approvalId,
                reason: payload.reason,
            });
        }
        return this.client.approvalsReject({
            approvalId: payload.approvalId,
            reason: payload.reason ?? "",
        });
    }
    async audit(result) {
        await (0, promises_1.mkdir)(RUNTIME_DIR, { recursive: true });
        await (0, promises_1.appendFile)(exports.APPROVAL_ACTION_AUDIT_LOG_PATH, `${JSON.stringify(result)}\n`, "utf8");
        return result;
    }
}
exports.ApprovalActionService = ApprovalActionService;
function runtimeApprovalGate() {
    return {
        readonlyMode: config_1.READONLY_MODE,
        actionsEnabled: config_1.APPROVAL_ACTIONS_ENABLED,
        dryRun: config_1.APPROVAL_ACTIONS_DRY_RUN,
    };
}
