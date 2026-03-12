"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.readMonitorLagSummary = readMonitorLagSummary;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const TIMELINE_LOG_PATH = (0, node_path_1.join)(process.cwd(), "runtime", "timeline.log");
async function readMonitorLagSummary(expectedIntervalMs, now = new Date()) {
    const safeExpected = Number.isFinite(expectedIntervalMs) && expectedIntervalMs > 0 ? expectedIntervalMs : 5000;
    const lastTickAt = await readLastMonitorTickAt();
    if (!lastTickAt) {
        return {
            generatedAt: now.toISOString(),
            expectedIntervalMs: safeExpected,
            status: "missing",
            sourcePath: TIMELINE_LOG_PATH,
        };
    }
    const lagMs = Math.max(0, now.getTime() - Date.parse(lastTickAt));
    let status = "ok";
    if (lagMs > safeExpected * 6) {
        status = "stale";
    }
    else if (lagMs > safeExpected * 2) {
        status = "warn";
    }
    return {
        generatedAt: now.toISOString(),
        lastTickAt,
        expectedIntervalMs: safeExpected,
        lagMs,
        status,
        sourcePath: TIMELINE_LOG_PATH,
    };
}
async function readLastMonitorTickAt() {
    try {
        const raw = await (0, promises_1.readFile)(TIMELINE_LOG_PATH, "utf8");
        const lines = raw
            .split(/\r?\n/)
            .map((line) => line.trim())
            .filter((line) => line.length > 0);
        for (let idx = lines.length - 1; idx >= 0; idx -= 1) {
            const match = lines[idx].match(/^(\S+)\s+\|\s+/);
            if (!match)
                continue;
            const ms = Date.parse(match[1]);
            if (Number.isNaN(ms))
                continue;
            return new Date(ms).toISOString();
        }
        return undefined;
    }
    catch {
        return undefined;
    }
}
