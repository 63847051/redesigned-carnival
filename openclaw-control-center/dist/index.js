"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const openclaw_readonly_1 = require("./adapters/openclaw-readonly");
const factory_1 = require("./clients/factory");
const config_1 = require("./config");
const export_bundle_1 = require("./runtime/export-bundle");
const import_dry_run_1 = require("./runtime/import-dry-run");
const monitor_1 = require("./runtime/monitor");
const notification_center_1 = require("./runtime/notification-center");
const operation_audit_1 = require("./runtime/operation-audit");
const task_heartbeat_1 = require("./runtime/task-heartbeat");
const server_1 = require("./ui/server");
const CONTINUOUS_MODE = process.env.MONITOR_CONTINUOUS === "true";
const UI_MODE = process.env.UI_MODE === "true";
const UI_PORT = Number.parseInt(process.env.UI_PORT ?? "4310", 10);
const COMMAND = normalizeCommand(process.env.APP_COMMAND ?? process.argv[2]);
const COMMAND_ARG = process.env.COMMAND_ARG ??
    (process.env.APP_COMMAND ? process.argv[2] : process.argv[3]);
async function start() {
    const client = (0, factory_1.createToolClient)();
    const adapter = new openclaw_readonly_1.OpenClawReadonlyAdapter(client);
    console.log("[mission-control] startup", {
        gateway: config_1.GATEWAY_URL,
        readonlyMode: config_1.READONLY_MODE,
        approvalActionsEnabled: config_1.APPROVAL_ACTIONS_ENABLED,
        approvalActionsDryRun: config_1.APPROVAL_ACTIONS_DRY_RUN,
        importMutationEnabled: config_1.IMPORT_MUTATION_ENABLED,
        importMutationDryRun: config_1.IMPORT_MUTATION_DRY_RUN,
        localTokenAuthRequired: config_1.LOCAL_TOKEN_AUTH_REQUIRED,
        localTokenConfigured: config_1.LOCAL_API_TOKEN !== "",
        taskHeartbeat: {
            enabled: config_1.TASK_HEARTBEAT_ENABLED,
            dryRun: config_1.TASK_HEARTBEAT_DRY_RUN,
            maxTasksPerRun: config_1.TASK_HEARTBEAT_MAX_TASKS_PER_RUN,
        },
        pollingIntervalsMs: config_1.POLLING_INTERVALS_MS,
        networkCalls: !config_1.READONLY_MODE,
        continuousMode: CONTINUOUS_MODE,
        command: COMMAND ?? "monitor",
    });
    if (COMMAND) {
        await runCommand(COMMAND, adapter, COMMAND_ARG);
        return;
    }
    await (0, monitor_1.runMonitorOnce)(adapter);
    if (CONTINUOUS_MODE) {
        const intervalMs = (0, monitor_1.monitorIntervalMs)();
        setInterval(() => {
            void (0, monitor_1.runMonitorOnce)(adapter);
        }, intervalMs);
    }
    if (UI_MODE) {
        (0, server_1.startUiServer)(UI_PORT, client);
    }
}
void start();
async function runCommand(command, adapter, arg) {
    assertCommandOperationGate(command);
    if (command === "backup-export") {
        try {
            const snapshot = await adapter.snapshot();
            const bundle = await (0, export_bundle_1.buildExportBundle)(snapshot, "command", "cmd-backup-export");
            const written = await (0, export_bundle_1.writeExportBundle)(bundle, "backup");
            await (0, operation_audit_1.appendOperationAudit)({
                action: "backup_export",
                source: "command",
                ok: true,
                requestId: "cmd-backup-export",
                detail: `wrote ${written.fileName}`,
                metadata: {
                    path: written.path,
                    sizeBytes: written.sizeBytes,
                },
            });
            console.log("[mission-control] backup export", {
                exportedAt: bundle.exportedAt,
                snapshotGeneratedAt: bundle.snapshotGeneratedAt,
                fileName: written.fileName,
                path: written.path,
                sizeBytes: written.sizeBytes,
            });
        }
        catch (error) {
            await (0, operation_audit_1.appendOperationAudit)({
                action: "backup_export",
                source: "command",
                ok: false,
                requestId: "cmd-backup-export",
                detail: error instanceof Error ? error.message : "backup export failed",
            });
            throw error;
        }
        return;
    }
    if (command === "acks-prune") {
        const dryRun = resolveAcksPruneDryRun(arg);
        try {
            const result = await (0, notification_center_1.pruneStaleAcks)({ dryRun });
            await (0, operation_audit_1.appendOperationAudit)({
                action: "ack_prune",
                source: "command",
                ok: true,
                requestId: "cmd-acks-prune",
                detail: `removed ${result.removed} stale ack(s)`,
                metadata: {
                    dryRun,
                    before: result.before,
                    removed: result.removed,
                    after: result.after,
                },
            });
            console.log("[mission-control] acks prune", result);
        }
        catch (error) {
            await (0, operation_audit_1.appendOperationAudit)({
                action: "ack_prune",
                source: "command",
                ok: false,
                requestId: "cmd-acks-prune",
                detail: error instanceof Error ? error.message : "acks prune failed",
            });
            throw error;
        }
        return;
    }
    if (command === "task-heartbeat") {
        const gate = (0, task_heartbeat_1.runtimeTaskHeartbeatGate)();
        const runDryRun = resolveTaskHeartbeatDryRun(arg, gate.dryRun);
        const result = await (0, task_heartbeat_1.runTaskHeartbeat)({
            gate: {
                ...gate,
                dryRun: runDryRun,
            },
        });
        await (0, operation_audit_1.appendOperationAudit)({
            action: "task_heartbeat",
            source: "command",
            ok: result.ok,
            requestId: "cmd-task-heartbeat",
            detail: `${result.mode} ${result.message}`,
            metadata: {
                checked: result.checked,
                eligible: result.eligible,
                selected: result.selected,
                executed: result.executed,
                dryRun: result.gate.dryRun,
            },
        });
        console.log("[mission-control] task heartbeat", result);
        if (!result.ok) {
            process.exitCode = 1;
        }
        return;
    }
    if (!arg) {
        throw new Error("import-validate requires a file path argument. Example: APP_COMMAND=import-validate COMMAND_ARG=<file.json> npm run dev");
    }
    const validation = await (0, import_dry_run_1.validateExportFileDryRun)(arg);
    await (0, operation_audit_1.appendOperationAudit)({
        action: "import_dry_run",
        source: "command",
        ok: validation.valid,
        requestId: "cmd-import-validate",
        detail: `validated ${validation.source}`,
        metadata: {
            valid: validation.valid,
            issues: validation.issues.length,
            warnings: validation.warnings.length,
        },
    });
    console.log("[mission-control] import dry-run", validation);
    if (!validation.valid) {
        process.exitCode = 1;
    }
}
function assertCommandOperationGate(command) {
    if (!config_1.LOCAL_TOKEN_AUTH_REQUIRED)
        return;
    if (config_1.LOCAL_API_TOKEN !== "")
        return;
    throw new Error(`${command} is blocked by local token gate. Set LOCAL_API_TOKEN to explicitly allow protected command execution.`);
}
function normalizeCommand(input) {
    if (!input)
        return undefined;
    const trimmed = input.trim().toLowerCase();
    if (trimmed === "")
        return undefined;
    if (trimmed === "backup-export")
        return "backup-export";
    if (trimmed === "import-validate")
        return "import-validate";
    if (trimmed === "acks-prune")
        return "acks-prune";
    if (trimmed === "task-heartbeat")
        return "task-heartbeat";
    throw new Error(`Unknown command '${input}'. Supported: backup-export, import-validate, acks-prune, task-heartbeat.`);
}
function resolveAcksPruneDryRun(arg) {
    const envDryRun = process.env.ACK_PRUNE_DRY_RUN === "true";
    if (!arg)
        return envDryRun;
    const normalized = arg.trim().toLowerCase();
    if (normalized === "" || normalized === "--live" || normalized === "live")
        return false;
    if (normalized === "--dry-run" || normalized === "dry-run")
        return true;
    throw new Error("acks-prune optional arg must be one of: --dry-run, dry-run, --live, live.");
}
function resolveTaskHeartbeatDryRun(arg, fallback) {
    if (!arg)
        return fallback;
    const normalized = arg.trim().toLowerCase();
    if (normalized === "")
        return fallback;
    if (normalized === "--dry-run" || normalized === "dry-run")
        return true;
    if (normalized === "--live" || normalized === "live")
        return false;
    throw new Error("task-heartbeat optional arg must be one of: --dry-run, dry-run, --live, live.");
}
