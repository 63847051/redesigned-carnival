"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.writeCommanderDigest = writeCommanderDigest;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const commander_1 = require("./commander");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
const DIGEST_DIR = (0, node_path_1.join)(RUNTIME_DIR, "digests");
async function writeCommanderDigest(snapshot, alerts) {
    const digest = buildCommanderDigest(snapshot, alerts);
    const jsonPath = (0, node_path_1.join)(DIGEST_DIR, `${digest.date}.json`);
    const markdownPath = (0, node_path_1.join)(DIGEST_DIR, `${digest.date}.md`);
    await (0, promises_1.mkdir)(DIGEST_DIR, { recursive: true });
    await Promise.all([
        (0, promises_1.writeFile)(jsonPath, `${JSON.stringify(digest, null, 2)}\n`, "utf8"),
        (0, promises_1.writeFile)(markdownPath, `${renderDigestMarkdown(digest)}\n`, "utf8"),
    ]);
    return {
        jsonPath,
        markdownPath,
        digest,
    };
}
function buildCommanderDigest(snapshot, alerts) {
    const generatedAt = new Date().toISOString();
    const date = generatedAt.slice(0, 10);
    const exceptions = (0, commander_1.commanderExceptions)(snapshot);
    const feed = (0, commander_1.commanderExceptionsFeed)(snapshot);
    const usage = snapshot.statuses.reduce((acc, status) => {
        acc.totalTokensIn += status.tokensIn ?? 0;
        acc.totalTokensOut += status.tokensOut ?? 0;
        acc.totalCost += status.cost ?? 0;
        return acc;
    }, {
        statuses: snapshot.statuses.length,
        totalTokensIn: 0,
        totalTokensOut: 0,
        totalCost: 0,
    });
    return {
        date,
        generatedAt,
        snapshotGeneratedAt: snapshot.generatedAt,
        sessions: {
            total: snapshot.sessions.length,
            byState: countBy(snapshot.sessions.map((session) => session.state)),
        },
        usage,
        approvals: {
            total: snapshot.approvals.length,
            pending: snapshot.approvals.filter((item) => item.status === "pending").length,
            approved: snapshot.approvals.filter((item) => item.status === "approved").length,
            denied: snapshot.approvals.filter((item) => item.status === "denied").length,
            unknown: snapshot.approvals.filter((item) => item.status === "unknown").length,
        },
        projects: {
            total: snapshot.projects.projects.length,
            byStatus: countBy(snapshot.projects.projects.map((project) => project.status)),
        },
        tasks: {
            total: snapshot.tasksSummary.tasks,
            todo: snapshot.tasksSummary.todo,
            inProgress: snapshot.tasksSummary.inProgress,
            blocked: snapshot.tasksSummary.blocked,
            done: snapshot.tasksSummary.done,
            dueNow: exceptions.counts.tasksDue,
        },
        budgets: {
            total: snapshot.budgetSummary.total,
            ok: snapshot.budgetSummary.ok,
            warn: snapshot.budgetSummary.warn,
            over: snapshot.budgetSummary.over,
        },
        alerts,
        exceptions: {
            counts: {
                blocked: exceptions.counts.blocked,
                errors: exceptions.counts.errors,
                pendingApprovals: exceptions.counts.pendingApprovals,
                overBudget: exceptions.counts.overBudget,
                tasksDue: exceptions.counts.tasksDue,
                info: feed.counts.info,
                warn: feed.counts.warn,
                actionRequired: feed.counts.actionRequired,
            },
            topItems: feed.items.slice(0, 20).map((item) => ({
                level: item.level,
                code: item.code,
                source: item.source,
                sourceId: item.sourceId,
                route: item.route,
                message: item.message,
            })),
        },
    };
}
function renderDigestMarkdown(digest) {
    const lines = [];
    lines.push(`# Commander Digest ${digest.date}`);
    lines.push("");
    lines.push(`Generated: ${digest.generatedAt}`);
    lines.push(`Snapshot: ${digest.snapshotGeneratedAt}`);
    lines.push("");
    lines.push("## Snapshot");
    lines.push(`- sessions: ${digest.sessions.total}`);
    lines.push(`- statuses: ${digest.usage.statuses}`);
    lines.push(`- tokens: in=${digest.usage.totalTokensIn} out=${digest.usage.totalTokensOut}`);
    lines.push(`- cost: ${digest.usage.totalCost.toFixed(4)}`);
    lines.push(`- projects: ${digest.projects.total}`);
    lines.push(`- tasks: total=${digest.tasks.total} todo=${digest.tasks.todo} in_progress=${digest.tasks.inProgress} blocked=${digest.tasks.blocked} done=${digest.tasks.done} due=${digest.tasks.dueNow}`);
    lines.push(`- approvals: total=${digest.approvals.total} pending=${digest.approvals.pending} approved=${digest.approvals.approved} denied=${digest.approvals.denied} unknown=${digest.approvals.unknown}`);
    lines.push(`- budgets: total=${digest.budgets.total} ok=${digest.budgets.ok} warn=${digest.budgets.warn} over=${digest.budgets.over}`);
    lines.push("");
    lines.push("## Session States");
    lines.push(...renderKeyValueList(digest.sessions.byState));
    lines.push("");
    lines.push("## Project States");
    lines.push(...renderKeyValueList(digest.projects.byStatus));
    lines.push("");
    lines.push("## Alerts");
    if (digest.alerts.length === 0) {
        lines.push("- none");
    }
    else {
        for (const alert of digest.alerts) {
            lines.push(`- [${alert.level}] ${alert.code}: ${alert.message} (route=${alert.route})`);
        }
    }
    lines.push("");
    lines.push("## Exceptions");
    lines.push(`- blocked=${digest.exceptions.counts.blocked} errors=${digest.exceptions.counts.errors} pending_approvals=${digest.exceptions.counts.pendingApprovals} over_budget=${digest.exceptions.counts.overBudget} tasks_due=${digest.exceptions.counts.tasksDue}`);
    lines.push(`- feed: info=${digest.exceptions.counts.info} warn=${digest.exceptions.counts.warn} action_required=${digest.exceptions.counts.actionRequired}`);
    lines.push("");
    lines.push("### Top Items");
    if (digest.exceptions.topItems.length === 0) {
        lines.push("- none");
    }
    else {
        for (const item of digest.exceptions.topItems) {
            lines.push(`- [${item.level}] ${item.code} ${item.source}:${item.sourceId} route=${item.route} ${item.message}`);
        }
    }
    return lines.join("\n");
}
function renderKeyValueList(input) {
    const keys = Object.keys(input).sort((a, b) => a.localeCompare(b));
    if (keys.length === 0)
        return ["- none"];
    return keys.map((key) => `- ${key}: ${input[key]}`);
}
function countBy(values) {
    const out = {};
    for (const value of values) {
        out[value] = (out[value] ?? 0) + 1;
    }
    return out;
}
