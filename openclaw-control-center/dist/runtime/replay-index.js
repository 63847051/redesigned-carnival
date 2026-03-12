"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadReplayIndex = loadReplayIndex;
exports.writeExportSnapshot = writeExportSnapshot;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const node_perf_hooks_1 = require("node:perf_hooks");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
const TIMELINE_LOG_PATH = (0, node_path_1.join)(RUNTIME_DIR, "timeline.log");
const DIGEST_DIR = (0, node_path_1.join)(RUNTIME_DIR, "digests");
const EXPORT_SNAPSHOT_DIR = (0, node_path_1.join)(RUNTIME_DIR, "export-snapshots");
const EXPORT_BUNDLES_DIR = (0, node_path_1.join)(RUNTIME_DIR, "exports");
async function loadReplayIndex(options = {}) {
    const window = parseReplayWindow(options.from, options.to);
    const resolved = {
        timelineLimit: options.timelineLimit ?? 80,
        digestLimit: options.digestLimit ?? 30,
        exportLimit: options.exportLimit ?? 30,
        from: window.fromIso,
        to: window.toIso,
    };
    const [timeline, digests, exportSnapshots, exportBundles] = await Promise.all([
        loadTimelineEntries(resolved.timelineLimit, window),
        loadDigestEntries(resolved.digestLimit, window),
        loadExportArtifacts(EXPORT_SNAPSHOT_DIR, resolved.exportLimit, window),
        loadExportArtifacts(EXPORT_BUNDLES_DIR, resolved.exportLimit, window),
    ]);
    const totalLatencySamplesMs = [
        ...timeline.latencySamplesMs,
        ...digests.latencySamplesMs,
        ...exportSnapshots.latencySamplesMs,
        ...exportBundles.latencySamplesMs,
    ];
    const stats = {
        timeline: timeline.stats,
        digests: digests.stats,
        exportSnapshots: exportSnapshots.stats,
        exportBundles: exportBundles.stats,
        total: sumReplayFilterStats([
            timeline.stats,
            digests.stats,
            exportSnapshots.stats,
            exportBundles.stats,
        ], totalLatencySamplesMs),
    };
    return {
        generatedAt: new Date().toISOString(),
        window: typeof resolved.from === "string" || typeof resolved.to === "string"
            ? {
                from: resolved.from,
                to: resolved.to,
            }
            : undefined,
        timeline: {
            path: timeline.path,
            totalLines: timeline.totalLines,
            entries: timeline.entries,
        },
        digests: digests.entries,
        exportSnapshots: exportSnapshots.entries,
        exportBundles: exportBundles.entries,
        stats,
    };
}
async function writeExportSnapshot(payload, requestId) {
    await (0, promises_1.mkdir)(EXPORT_SNAPSHOT_DIR, { recursive: true });
    const stamp = new Date().toISOString().replace(/[-:.]/g, "").replace("T", "-").slice(0, 19);
    const safeRequestId = requestId.replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 40) || "unknown";
    const fileName = `${stamp}-${safeRequestId}.json`;
    const path = (0, node_path_1.join)(EXPORT_SNAPSHOT_DIR, fileName);
    const body = `${JSON.stringify(payload, null, 2)}\n`;
    await (0, promises_1.writeFile)(path, body, "utf8");
    return {
        fileName,
        path,
        sizeBytes: Buffer.byteLength(body, "utf8"),
    };
}
async function loadTimelineEntries(limit, window) {
    const startedAt = node_perf_hooks_1.performance.now();
    const raw = await safeReadFile(TIMELINE_LOG_PATH);
    const lines = raw
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter((line) => line !== "");
    const parsed = lines.map((line) => {
        const parseStartedAt = node_perf_hooks_1.performance.now();
        const sizeBytes = Buffer.byteLength(line, "utf8");
        const match = line.match(/^(\S+)\s+\|\s+(.*)$/);
        if (!match) {
            return {
                sizeBytes,
                parseLatencyMs: node_perf_hooks_1.performance.now() - parseStartedAt,
                entry: {
                    timestamp: "",
                    summary: line,
                },
            };
        }
        const timestamp = !Number.isNaN(Date.parse(match[1]))
            ? new Date(match[1]).toISOString()
            : match[1];
        return {
            timestampMs: parseTimestampMs(timestamp),
            sizeBytes,
            parseLatencyMs: node_perf_hooks_1.performance.now() - parseStartedAt,
            entry: {
                timestamp,
                summary: match[2],
            },
        };
    });
    const within = parsed.filter((item) => withinWindow(item.timestampMs, window));
    const limited = within.slice(-limit);
    const entries = limited.reverse().map((item) => item.entry);
    const totalSizeBytes = parsed.reduce((sum, item) => sum + item.sizeBytes, 0);
    const returnedSizeBytes = limited.reduce((sum, item) => sum + item.sizeBytes, 0);
    return {
        path: TIMELINE_LOG_PATH,
        totalLines: lines.length,
        entries,
        stats: buildReplayFilterStats(parsed.length, within.length, entries.length, {
            latencyMs: node_perf_hooks_1.performance.now() - startedAt,
            latencySamplesMs: parsed.map((item) => item.parseLatencyMs),
            totalSizeBytes,
            returnedSizeBytes,
        }),
        latencySamplesMs: parsed.map((item) => item.parseLatencyMs),
    };
}
async function loadDigestEntries(limit, window) {
    const startedAt = node_perf_hooks_1.performance.now();
    let files = [];
    try {
        files = await (0, promises_1.readdir)(DIGEST_DIR);
    }
    catch {
        return emptyReplayCollection();
    }
    const markdownSet = new Set(files.filter((name) => name.endsWith(".md")));
    const jsonFiles = files.filter((name) => name.endsWith(".json")).sort((a, b) => b.localeCompare(a));
    const parsed = await Promise.all(jsonFiles.map(async (name) => {
        const itemStartedAt = node_perf_hooks_1.performance.now();
        const path = (0, node_path_1.join)(DIGEST_DIR, name);
        const digest = await safeReadJson(path);
        const digestDate = asString(digest?.date) ?? name.slice(0, -5);
        const markdownName = `${digestDate}.md`;
        const fileStat = await safeStat(path);
        const timestampMs = parseTimestampMs(asString(digest?.generatedAt)) ??
            parseTimestampMs(asString(digest?.snapshotGeneratedAt)) ??
            parseTimestampMs(digestDate);
        return {
            timestampMs,
            loadLatencyMs: node_perf_hooks_1.performance.now() - itemStartedAt,
            entry: {
                date: digestDate,
                jsonPath: path,
                markdownPath: markdownSet.has(markdownName) ? (0, node_path_1.join)(DIGEST_DIR, markdownName) : undefined,
                generatedAt: asString(digest?.generatedAt),
                snapshotGeneratedAt: asString(digest?.snapshotGeneratedAt),
                sizeBytes: fileStat?.size ?? 0,
            },
        };
    }));
    const within = parsed.filter((item) => withinWindow(item.timestampMs, window));
    const limited = within.slice(0, limit);
    const entries = limited.map((item) => item.entry);
    const totalSizeBytes = parsed.reduce((sum, item) => sum + item.entry.sizeBytes, 0);
    const returnedSizeBytes = limited.reduce((sum, item) => sum + item.entry.sizeBytes, 0);
    return {
        entries,
        stats: buildReplayFilterStats(parsed.length, within.length, entries.length, {
            latencyMs: node_perf_hooks_1.performance.now() - startedAt,
            latencySamplesMs: parsed.map((item) => item.loadLatencyMs),
            totalSizeBytes,
            returnedSizeBytes,
        }),
        latencySamplesMs: parsed.map((item) => item.loadLatencyMs),
    };
}
async function loadExportArtifacts(dirPath, limit, window) {
    const startedAt = node_perf_hooks_1.performance.now();
    let files = [];
    try {
        files = await (0, promises_1.readdir)(dirPath);
    }
    catch {
        return emptyReplayCollection();
    }
    const jsonFiles = files.filter((name) => name.endsWith(".json")).sort((a, b) => b.localeCompare(a));
    const parsed = await Promise.all(jsonFiles.map(async (name) => {
        const itemStartedAt = node_perf_hooks_1.performance.now();
        const path = (0, node_path_1.join)(dirPath, name);
        const raw = await safeReadJson(path);
        const fileStat = await safeStat(path);
        const projects = asArray(asObject(raw?.projects)?.projects).length;
        const tasks = asArray(asObject(raw?.tasks)?.tasks).length;
        const sessions = asArray(raw?.sessions).length;
        const exceptions = asArray(asObject(raw?.exceptionsFeed)?.items).length;
        const exportedAt = asString(raw?.exportedAt);
        const snapshotGeneratedAt = asString(raw?.snapshotGeneratedAt);
        const timestampMs = parseTimestampMs(exportedAt) ?? parseTimestampMs(snapshotGeneratedAt);
        return {
            timestampMs,
            loadLatencyMs: node_perf_hooks_1.performance.now() - itemStartedAt,
            entry: {
                fileName: name,
                path,
                sizeBytes: fileStat?.size ?? 0,
                exportedAt,
                snapshotGeneratedAt,
                requestId: asString(raw?.requestId),
                counts: {
                    projects,
                    tasks,
                    sessions,
                    exceptions,
                },
            },
        };
    }));
    const within = parsed.filter((item) => withinWindow(item.timestampMs, window));
    const limited = within.slice(0, limit);
    const entries = limited.map((item) => item.entry);
    const totalSizeBytes = parsed.reduce((sum, item) => sum + item.entry.sizeBytes, 0);
    const returnedSizeBytes = limited.reduce((sum, item) => sum + item.entry.sizeBytes, 0);
    return {
        entries,
        stats: buildReplayFilterStats(parsed.length, within.length, entries.length, {
            latencyMs: node_perf_hooks_1.performance.now() - startedAt,
            latencySamplesMs: parsed.map((item) => item.loadLatencyMs),
            totalSizeBytes,
            returnedSizeBytes,
        }),
        latencySamplesMs: parsed.map((item) => item.loadLatencyMs),
    };
}
function parseReplayWindow(from, to) {
    const fromMs = parseTimestampMs(from);
    const toMs = parseTimestampMs(to);
    if (from && fromMs === undefined) {
        throw new Error(`Invalid replay from timestamp '${from}'.`);
    }
    if (to && toMs === undefined) {
        throw new Error(`Invalid replay to timestamp '${to}'.`);
    }
    if (typeof fromMs === "number" && typeof toMs === "number" && fromMs > toMs) {
        throw new Error("Invalid replay window: from must be less than or equal to to.");
    }
    return {
        fromMs,
        toMs,
        fromIso: typeof fromMs === "number" ? new Date(fromMs).toISOString() : undefined,
        toIso: typeof toMs === "number" ? new Date(toMs).toISOString() : undefined,
    };
}
function withinWindow(timestampMs, window) {
    if (window.fromMs === undefined && window.toMs === undefined)
        return true;
    if (timestampMs === undefined)
        return false;
    if (window.fromMs !== undefined && timestampMs < window.fromMs)
        return false;
    if (window.toMs !== undefined && timestampMs > window.toMs)
        return false;
    return true;
}
function emptyReplayCollection() {
    return {
        entries: [],
        stats: buildReplayFilterStats(0, 0, 0),
        latencySamplesMs: [],
    };
}
function buildReplayFilterStats(total, withinWindowCount, returned, extra = {}) {
    const filteredOutByWindow = Math.max(0, total - withinWindowCount);
    const filteredOutByLimit = Math.max(0, withinWindowCount - returned);
    const normalizedLatencySamples = normalizeLatencySamples(extra.latencySamplesMs);
    return {
        total,
        returned,
        filteredOut: Math.max(0, total - returned),
        filteredOutByWindow,
        filteredOutByLimit,
        latencyMs: Math.max(0, Math.round(extra.latencyMs ?? 0)),
        latencyBucketsMs: buildReplayLatencyBuckets(normalizedLatencySamples),
        totalSizeBytes: Math.max(0, Math.round(extra.totalSizeBytes ?? 0)),
        returnedSizeBytes: Math.max(0, Math.round(extra.returnedSizeBytes ?? 0)),
    };
}
function sumReplayFilterStats(stats, latencySamplesMs = []) {
    const summed = stats.reduce((acc, item) => ({
        total: acc.total + item.total,
        returned: acc.returned + item.returned,
        filteredOut: acc.filteredOut + item.filteredOut,
        filteredOutByWindow: acc.filteredOutByWindow + item.filteredOutByWindow,
        filteredOutByLimit: acc.filteredOutByLimit + item.filteredOutByLimit,
        latencyMs: acc.latencyMs + item.latencyMs,
        latencyBucketsMs: acc.latencyBucketsMs,
        totalSizeBytes: acc.totalSizeBytes + item.totalSizeBytes,
        returnedSizeBytes: acc.returnedSizeBytes + item.returnedSizeBytes,
    }), buildReplayFilterStats(0, 0, 0));
    return {
        ...summed,
        latencyBucketsMs: buildReplayLatencyBuckets(normalizeLatencySamples(latencySamplesMs)),
    };
}
function normalizeLatencySamples(input) {
    if (!Array.isArray(input))
        return [];
    return input
        .filter((value) => Number.isFinite(value))
        .map((value) => Math.max(0, value));
}
function buildReplayLatencyBuckets(samples) {
    return {
        p50: percentile(samples, 50),
        p95: percentile(samples, 95),
    };
}
function percentile(samples, target) {
    if (samples.length === 0)
        return 0;
    const sorted = [...samples].sort((a, b) => a - b);
    const rank = (Math.min(100, Math.max(0, target)) / 100) * (sorted.length - 1);
    const lower = Math.floor(rank);
    const upper = Math.ceil(rank);
    if (lower === upper)
        return Math.max(0, Math.round(sorted[lower]));
    const weight = rank - lower;
    return Math.max(0, Math.round(sorted[lower] + (sorted[upper] - sorted[lower]) * weight));
}
function parseTimestampMs(input) {
    if (typeof input !== "string" || input.trim() === "")
        return undefined;
    const parsed = Date.parse(input);
    return Number.isNaN(parsed) ? undefined : parsed;
}
async function safeReadFile(path) {
    try {
        return await (0, promises_1.readFile)(path, "utf8");
    }
    catch {
        return "";
    }
}
async function safeReadJson(path) {
    try {
        const text = await (0, promises_1.readFile)(path, "utf8");
        const parsed = JSON.parse(text);
        return asObject(parsed);
    }
    catch {
        return undefined;
    }
}
async function safeStat(path) {
    try {
        const fileStat = await (0, promises_1.stat)(path);
        return { size: fileStat.size };
    }
    catch {
        return undefined;
    }
}
function asString(input) {
    return typeof input === "string" ? input : undefined;
}
function asObject(input) {
    return input !== null && typeof input === "object" && !Array.isArray(input)
        ? input
        : undefined;
}
function asArray(input) {
    return Array.isArray(input) ? input : [];
}
