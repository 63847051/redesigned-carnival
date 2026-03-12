"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.saveSnapshot = saveSnapshot;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
const LAST_SNAPSHOT_PATH = (0, node_path_1.join)(RUNTIME_DIR, "last-snapshot.json");
function countOf(items) {
    return Array.isArray(items) ? items.length : 0;
}
function computeDiff(prev, next) {
    if (!prev) {
        return {
            sessionsDelta: countOf(next.sessions),
            statusesDelta: countOf(next.statuses),
            cronJobsDelta: countOf(next.cronJobs),
            approvalsDelta: countOf(next.approvals),
            projectsDelta: countOf(next.projects.projects),
            tasksDelta: next.tasksSummary.tasks,
            budgetEvaluationsDelta: next.budgetSummary.total,
        };
    }
    const prevTasks = prev.tasksSummary?.tasks ?? 0;
    const prevBudgets = prev.budgetSummary?.total ?? 0;
    return {
        sessionsDelta: countOf(next.sessions) - countOf(prev.sessions),
        statusesDelta: countOf(next.statuses) - countOf(prev.statuses),
        cronJobsDelta: countOf(next.cronJobs) - countOf(prev.cronJobs),
        approvalsDelta: countOf(next.approvals) - countOf(prev.approvals),
        projectsDelta: countOf(next.projects.projects) - countOf(prev.projects?.projects),
        tasksDelta: next.tasksSummary.tasks - prevTasks,
        budgetEvaluationsDelta: next.budgetSummary.total - prevBudgets,
    };
}
async function readPreviousSnapshot() {
    for (let attempt = 0; attempt < 3; attempt += 1) {
        try {
            const raw = await (0, promises_1.readFile)(LAST_SNAPSHOT_PATH, "utf8");
            return JSON.parse(raw);
        }
        catch {
            if (attempt === 2)
                return null;
            await delay(25 * (attempt + 1));
        }
    }
    return null;
}
async function saveSnapshot(next) {
    const prev = await readPreviousSnapshot();
    const diff = computeDiff(prev, next);
    await (0, promises_1.mkdir)((0, node_path_1.dirname)(LAST_SNAPSHOT_PATH), { recursive: true });
    const tempPath = `${LAST_SNAPSHOT_PATH}.tmp-${process.pid}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    await (0, promises_1.writeFile)(tempPath, JSON.stringify(next, null, 2), "utf8");
    await (0, promises_1.rename)(tempPath, LAST_SNAPSHOT_PATH);
    return {
        path: LAST_SNAPSHOT_PATH,
        diff,
    };
}
function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
