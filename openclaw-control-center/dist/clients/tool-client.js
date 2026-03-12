"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReadonlyToolClient = void 0;
const config_1 = require("../config");
class ReadonlyToolClient {
    async sessionsList() {
        return { sessions: [] };
    }
    async sessionStatus(_sessionKey) {
        return { rawText: "" };
    }
    async sessionsHistory(_request) {
        return { rawText: "" };
    }
    async cronList() {
        return { jobs: [] };
    }
    async approvalsGet() {
        return { rawText: "" };
    }
    async approvalsApprove(request) {
        if (!config_1.APPROVAL_ACTIONS_ENABLED) {
            throw new Error(`approvalsApprove is disabled by safety gate (APPROVAL_ACTIONS_ENABLED=${String(config_1.APPROVAL_ACTIONS_ENABLED)}).`);
        }
        return {
            ok: false,
            action: "approve",
            approvalId: request.approvalId,
            reason: request.reason,
            rawText: "readonly client has no approve capability",
        };
    }
    async approvalsReject(request) {
        if (!config_1.APPROVAL_ACTIONS_ENABLED) {
            throw new Error(`approvalsReject is disabled by safety gate (APPROVAL_ACTIONS_ENABLED=${String(config_1.APPROVAL_ACTIONS_ENABLED)}).`);
        }
        return {
            ok: false,
            action: "reject",
            approvalId: request.approvalId,
            reason: request.reason,
            rawText: "readonly client has no reject capability",
        };
    }
}
exports.ReadonlyToolClient = ReadonlyToolClient;
