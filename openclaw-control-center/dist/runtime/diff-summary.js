"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.formatDiffSummary = formatDiffSummary;
function formatDiffSummary(diff) {
    const parts = [
        `sessions ${signed(diff.sessionsDelta)}`,
        `statuses ${signed(diff.statusesDelta)}`,
        `cronJobs ${signed(diff.cronJobsDelta)}`,
        `approvals ${signed(diff.approvalsDelta)}`,
        `projects ${signed(diff.projectsDelta)}`,
        `tasks ${signed(diff.tasksDelta)}`,
        `budgets ${signed(diff.budgetEvaluationsDelta)}`,
    ];
    return parts.join(" | ");
}
function signed(value) {
    if (value > 0)
        return `+${value}`;
    return `${value}`;
}
