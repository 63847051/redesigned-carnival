"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildCronOverview = buildCronOverview;
const monitor_health_1 = require("./monitor-health");
const task_heartbeat_1 = require("./task-heartbeat");
async function buildCronOverview(snapshot, monitorIntervalMs, now = new Date()) {
    const snapshotJobs = (snapshot.cronJobs ?? [])
        .map((job) => toCronJobOverview(job, now))
        .sort((a, b) => sortByNextRun(a.nextRunAt, b.nextRunAt));
    const monitor = await (0, monitor_health_1.readMonitorLagSummary)(monitorIntervalMs, now);
    const runtimeFallbackJobs = await buildRuntimeFallbackJobs(monitor, monitorIntervalMs, now);
    const jobs = mergeCronJobs(snapshotJobs, runtimeFallbackJobs).sort((a, b) => sortByNextRun(a.nextRunAt, b.nextRunAt));
    const counts = {
        scheduled: 0,
        due: 0,
        late: 0,
        unknown: 0,
        disabled: 0,
    };
    for (const job of jobs) {
        counts[job.health] += 1;
    }
    const nextRunAt = jobs
        .filter((job) => job.enabled && typeof job.nextRunAt === "string")
        .map((job) => job.nextRunAt)
        .sort((a, b) => Date.parse(a) - Date.parse(b))[0];
    const enabledJobs = jobs.filter((job) => job.enabled).length;
    const status = counts.late > 0 || counts.unknown > 0 || enabledJobs === 0 || monitor.status === "missing" || monitor.status === "stale"
        ? "warn"
        : "ok";
    return {
        generatedAt: now.toISOString(),
        snapshotGeneratedAt: snapshot.generatedAt,
        nextRunAt,
        jobs,
        counts,
        health: {
            status,
            enabledJobs,
            totalJobs: jobs.length,
            monitor,
        },
    };
}
async function buildRuntimeFallbackJobs(monitor, monitorIntervalMs, now) {
    const jobs = [];
    const monitorJob = buildRuntimeMonitorJob(monitor, now);
    if (monitorJob)
        jobs.push(monitorJob);
    const heartbeatJob = await buildRuntimeHeartbeatJob(monitorIntervalMs, now);
    if (heartbeatJob)
        jobs.push(heartbeatJob);
    return jobs;
}
function buildRuntimeMonitorJob(monitor, now) {
    if (!monitor.lastTickAt)
        return undefined;
    const intervalMs = Math.max(1000, monitor.expectedIntervalMs);
    const lastTickMs = Date.parse(monitor.lastTickAt);
    if (!Number.isFinite(lastTickMs))
        return undefined;
    const nextRunMs = lastTickMs + intervalMs;
    const dueInSeconds = Math.round((nextRunMs - now.getTime()) / 1000);
    const health = monitor.status === "ok" ? "scheduled" : monitor.status === "warn" ? "due" : "late";
    return {
        jobId: "runtime-monitor-loop",
        name: "Runtime monitor loop",
        enabled: true,
        nextRunAt: new Date(nextRunMs).toISOString(),
        dueInSeconds,
        health,
    };
}
async function buildRuntimeHeartbeatJob(monitorIntervalMs, now) {
    const runs = await (0, task_heartbeat_1.readTaskHeartbeatRuns)(1);
    const latest = runs.runs[0];
    if (!latest?.evaluatedAt)
        return undefined;
    const latestMs = Date.parse(latest.evaluatedAt);
    if (!Number.isFinite(latestMs))
        return undefined;
    const intervalMs = Math.max(1000, monitorIntervalMs);
    const nextRunMs = latestMs + intervalMs;
    const dueInSeconds = Math.round((nextRunMs - now.getTime()) / 1000);
    const lagMs = Math.max(0, now.getTime() - latestMs);
    const enabled = latest.gate.enabled;
    const health = !enabled
        ? "disabled"
        : lagMs <= intervalMs * 2
            ? "scheduled"
            : lagMs <= intervalMs * 6
                ? "due"
                : "late";
    return {
        jobId: "runtime-task-heartbeat-worker",
        name: "Task heartbeat worker",
        enabled,
        nextRunAt: new Date(nextRunMs).toISOString(),
        dueInSeconds,
        health,
    };
}
function mergeCronJobs(snapshotJobs, runtimeJobs) {
    if (runtimeJobs.length === 0)
        return snapshotJobs;
    const merged = [...snapshotJobs];
    const seen = new Set(snapshotJobs.map((job) => job.jobId.trim().toLowerCase()));
    for (const runtimeJob of runtimeJobs) {
        const key = runtimeJob.jobId.trim().toLowerCase();
        if (seen.has(key))
            continue;
        merged.push(runtimeJob);
        seen.add(key);
    }
    return merged;
}
function toCronJobOverview(job, now) {
    if (!job.enabled) {
        return {
            jobId: job.jobId,
            name: job.name,
            enabled: false,
            nextRunAt: job.nextRunAt,
            health: "disabled",
        };
    }
    const nextRunMs = job.nextRunAt ? Date.parse(job.nextRunAt) : Number.NaN;
    if (!Number.isFinite(nextRunMs)) {
        return {
            jobId: job.jobId,
            name: job.name,
            enabled: true,
            nextRunAt: job.nextRunAt,
            health: "unknown",
        };
    }
    const lagMs = nextRunMs - now.getTime();
    const dueInSeconds = Math.round(lagMs / 1000);
    let health = "scheduled";
    if (lagMs <= 0)
        health = "due";
    if (lagMs < -5 * 60 * 1000)
        health = "late";
    return {
        jobId: job.jobId,
        name: job.name,
        enabled: true,
        nextRunAt: new Date(nextRunMs).toISOString(),
        dueInSeconds,
        health,
    };
}
function sortByNextRun(left, right) {
    if (!left && !right)
        return 0;
    if (!left)
        return 1;
    if (!right)
        return -1;
    return Date.parse(left) - Date.parse(right);
}
