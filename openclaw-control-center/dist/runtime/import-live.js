"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.applyImportMutation = applyImportMutation;
exports.evaluateImportMutationGuard = evaluateImportMutationGuard;
exports.readImportMutationGuardState = readImportMutationGuardState;
exports.resolveImportInputForSmoke = resolveImportInputForSmoke;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const config_1 = require("../config");
const budget_policy_1 = require("./budget-policy");
const import_dry_run_1 = require("./import-dry-run");
const project_store_1 = require("./project-store");
const task_store_1 = require("./task-store");
async function applyImportMutation(request) {
    const gate = evaluateImportMutationGuard({
        mutationEnabled: config_1.IMPORT_MUTATION_ENABLED,
        mutationDryRunDefault: config_1.IMPORT_MUTATION_DRY_RUN,
        readonlyMode: config_1.READONLY_MODE,
        routeLabel: "/api/import/live",
        requestedDryRun: request.dryRun,
    });
    const guard = readImportMutationGuardState();
    if (!gate.ok) {
        return {
            ok: false,
            statusCode: gate.statusCode,
            mode: gate.mode,
            message: gate.message,
            guard,
        };
    }
    const loaded = await resolveImportInput(request);
    if (!loaded.ok) {
        return {
            ok: false,
            statusCode: 400,
            mode: gate.mode,
            message: loaded.message,
            validation: loaded.validation,
            guard,
            source: loaded.source,
        };
    }
    if (!loaded.validation.valid) {
        return {
            ok: false,
            statusCode: 400,
            mode: gate.mode,
            message: "Import payload validation failed.",
            validation: loaded.validation,
            guard,
            source: loaded.source,
        };
    }
    if (gate.mode === "dry_run") {
        return {
            ok: true,
            statusCode: 200,
            mode: gate.mode,
            message: "Import dry-run passed; no files were mutated.",
            validation: loaded.validation,
            guard,
            source: loaded.source,
        };
    }
    const root = asObject(loaded.bundle);
    if (!root) {
        return {
            ok: false,
            statusCode: 400,
            mode: gate.mode,
            message: "Import payload must be a JSON object.",
            validation: loaded.validation,
            guard,
            source: loaded.source,
        };
    }
    const projectsRoot = asObject(root.projects);
    const tasksRoot = asObject(root.tasks);
    const budgetsRoot = asObject(root.budgets);
    const policyRoot = asObject(budgetsRoot?.policy);
    if (!projectsRoot || !tasksRoot || !policyRoot) {
        return {
            ok: false,
            statusCode: 400,
            mode: gate.mode,
            message: "Import payload is missing required projects/tasks/budgets.policy objects.",
            validation: loaded.validation,
            guard,
            source: loaded.source,
        };
    }
    const [projectsPath, tasksPath, budgetsPath] = await Promise.all([
        (0, project_store_1.saveProjectStore)(projectsRoot),
        (0, task_store_1.saveTaskStore)(tasksRoot),
        writeBudgetPolicy(policyRoot),
    ]);
    return {
        ok: true,
        statusCode: 200,
        mode: gate.mode,
        message: "Import applied to local runtime stores.",
        validation: loaded.validation,
        guard,
        source: loaded.source,
        applied: {
            projectsPath,
            tasksPath,
            budgetsPath,
            projects: loaded.validation.summary.projects,
            tasks: loaded.validation.summary.tasks,
            sessions: loaded.validation.summary.sessions,
            exceptions: loaded.validation.summary.exceptions,
        },
    };
}
function evaluateImportMutationGuard(input) {
    const effectiveDryRun = input.requestedDryRun ?? input.mutationDryRunDefault;
    if (!input.mutationEnabled) {
        return {
            ok: false,
            statusCode: 403,
            mode: "blocked",
            dryRun: effectiveDryRun,
            message: `${input.routeLabel} is disabled. Set IMPORT_MUTATION_ENABLED=true to allow live import mutation endpoint usage.`,
        };
    }
    if (input.readonlyMode && !effectiveDryRun) {
        return {
            ok: false,
            statusCode: 403,
            mode: "blocked",
            dryRun: effectiveDryRun,
            message: `${input.routeLabel} is blocked by readonly mode. Set READONLY_MODE=false or send {\"dryRun\":true} for non-mutating validation mode.`,
        };
    }
    return {
        ok: true,
        statusCode: 200,
        mode: effectiveDryRun ? "dry_run" : "live",
        dryRun: effectiveDryRun,
        message: effectiveDryRun
            ? "Import mutation request accepted in dry-run mode."
            : "Import mutation request accepted in live mode.",
    };
}
function readImportMutationGuardState() {
    const decision = evaluateImportMutationGuard({
        mutationEnabled: config_1.IMPORT_MUTATION_ENABLED,
        mutationDryRunDefault: config_1.IMPORT_MUTATION_DRY_RUN,
        readonlyMode: config_1.READONLY_MODE,
        routeLabel: "/api/import/live",
    });
    return {
        readonlyMode: config_1.READONLY_MODE,
        localTokenAuthRequired: config_1.LOCAL_TOKEN_AUTH_REQUIRED,
        localTokenConfigured: config_1.LOCAL_API_TOKEN !== "",
        mutationEnabled: config_1.IMPORT_MUTATION_ENABLED,
        mutationDryRunDefault: config_1.IMPORT_MUTATION_DRY_RUN,
        defaultMode: decision.mode,
        defaultMessage: decision.message,
    };
}
async function resolveImportInput(request) {
    if (typeof request.fileName === "string" && request.fileName.trim() !== "") {
        let sourcePath = "";
        let source = `file:${request.fileName.trim()}`;
        try {
            sourcePath = (0, import_dry_run_1.resolveExportPath)(request.fileName);
            source = `file:${sourcePath}`;
        }
        catch (error) {
            const message = error instanceof Error ? error.message : "Failed to resolve import file.";
            return {
                ok: false,
                source,
                bundle: undefined,
                validation: {
                    validatedAt: new Date().toISOString(),
                    source,
                    valid: false,
                    issues: [message],
                    warnings: [],
                    summary: {
                        sessions: 0,
                        projects: 0,
                        tasks: 0,
                        exceptions: 0,
                    },
                },
                message,
            };
        }
        try {
            const raw = await (0, promises_1.readFile)(sourcePath, "utf8");
            const parsed = JSON.parse(raw);
            const validation = (0, import_dry_run_1.validateExportBundleDryRun)(parsed, source);
            if (!validation.valid) {
                return {
                    ok: false,
                    source,
                    bundle: undefined,
                    validation,
                    message: "Import payload validation failed.",
                };
            }
            return {
                ok: true,
                source,
                bundle: parsed,
                validation,
                message: "Import payload loaded from file.",
            };
        }
        catch (error) {
            const message = error instanceof Error ? error.message : "Failed to read import file.";
            return {
                ok: false,
                source,
                bundle: undefined,
                validation: {
                    validatedAt: new Date().toISOString(),
                    source,
                    valid: false,
                    issues: [message],
                    warnings: [],
                    summary: {
                        sessions: 0,
                        projects: 0,
                        tasks: 0,
                        exceptions: 0,
                    },
                },
                message,
            };
        }
    }
    const source = request.bundle !== undefined ? "payload.bundle" : "payload";
    const bundle = request.bundle !== undefined ? request.bundle : request;
    const validation = (0, import_dry_run_1.validateExportBundleDryRun)(bundle, source);
    if (!validation.valid) {
        return {
            ok: false,
            source,
            bundle: undefined,
            validation,
            message: "Import payload validation failed.",
        };
    }
    return {
        ok: true,
        source,
        bundle,
        validation,
        message: "Import payload loaded.",
    };
}
async function resolveImportInputForSmoke(request) {
    return resolveImportInput(request);
}
async function writeBudgetPolicy(policy) {
    await (0, promises_1.mkdir)((0, node_path_1.dirname)(budget_policy_1.BUDGET_POLICY_PATH), { recursive: true });
    await (0, promises_1.writeFile)(budget_policy_1.BUDGET_POLICY_PATH, `${JSON.stringify(policy, null, 2)}\n`, "utf8");
    return budget_policy_1.BUDGET_POLICY_PATH;
}
function asObject(input) {
    return input !== null && typeof input === "object" && !Array.isArray(input)
        ? input
        : undefined;
}
