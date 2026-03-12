"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.NotificationCenterValidationError = exports.ACKS_PATH = void 0;
exports.loadAcksStore = loadAcksStore;
exports.saveAcksStore = saveAcksStore;
exports.actionQueueItemId = actionQueueItemId;
exports.buildNotificationCenter = buildNotificationCenter;
exports.acknowledgeActionQueueItem = acknowledgeActionQueueItem;
exports.pruneStaleAcks = pruneStaleAcks;
exports.previewStaleAcksPrune = previewStaleAcksPrune;
exports.pruneStaleAcksFromStore = pruneStaleAcksFromStore;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const RUNTIME_DIR = (0, node_path_1.join)(process.cwd(), "runtime");
exports.ACKS_PATH = (0, node_path_1.join)(RUNTIME_DIR, "acks.json");
const EMPTY_ACKS = {
    acks: [],
    updatedAt: "1970-01-01T00:00:00.000Z",
};
class NotificationCenterValidationError extends Error {
    statusCode;
    issues;
    constructor(message, issues = [], statusCode = 400) {
        super(message);
        this.name = "NotificationCenterValidationError";
        this.statusCode = statusCode;
        this.issues = issues;
    }
}
exports.NotificationCenterValidationError = NotificationCenterValidationError;
async function loadAcksStore() {
    try {
        const raw = await (0, promises_1.readFile)(exports.ACKS_PATH, "utf8");
        return normalizeAcksStore(JSON.parse(raw));
    }
    catch {
        return cloneEmptyAcks();
    }
}
async function saveAcksStore(next) {
    const normalized = normalizeAcksStore({
        ...next,
        updatedAt: new Date().toISOString(),
    });
    await (0, promises_1.mkdir)(RUNTIME_DIR, { recursive: true });
    await (0, promises_1.writeFile)(exports.ACKS_PATH, JSON.stringify(normalized, null, 2), "utf8");
    return exports.ACKS_PATH;
}
function actionQueueItemId(item) {
    return `${item.code}:${item.source}:${item.sourceId}`;
}
function buildNotificationCenter(feed, ackStore, linksByItemId = new Map()) {
    const nowMs = Date.now();
    const ackByItemId = new Map(ackStore.acks.map((ack) => [ack.itemId, ack]));
    const queue = feed.items
        .filter((item) => item.route === "action-queue" || item.level === "action-required")
        .map((item) => {
        const itemId = actionQueueItemId(item);
        const ack = resolveActiveAck(ackByItemId.get(itemId), nowMs);
        return {
            ...item,
            itemId,
            acknowledged: Boolean(ack),
            ackedAt: ack?.ackedAt,
            note: ack?.note,
            ackExpiresAt: ack?.expiresAt,
            links: linksByItemId.get(itemId) ?? [],
        };
    });
    return {
        generatedAt: new Date().toISOString(),
        queue,
        counts: {
            total: queue.length,
            acked: queue.filter((item) => item.acknowledged).length,
            unacked: queue.filter((item) => !item.acknowledged).length,
        },
    };
}
async function acknowledgeActionQueueItem(input, center) {
    const payload = validateAcknowledgeInput(input);
    const target = center.queue.find((item) => item.itemId === payload.itemId);
    if (!target) {
        throw new NotificationCenterValidationError(`itemId '${payload.itemId}' was not found in the current action queue.`, ["itemId"], 404);
    }
    const ackStore = await loadAcksStore();
    const now = new Date().toISOString();
    const nowMs = Date.now();
    const expiresAt = resolveAckExpiresAt(payload, nowMs);
    const ack = {
        itemId: payload.itemId,
        ackedAt: now,
        note: payload.note,
        expiresAt,
    };
    const pruned = pruneStaleAcksFromStore(ackStore, nowMs);
    ackStore.acks = pruned.store.acks;
    const existingIdx = ackStore.acks.findIndex((item) => item.itemId === payload.itemId);
    if (existingIdx >= 0) {
        ackStore.acks[existingIdx] = ack;
    }
    else {
        ackStore.acks.push(ack);
    }
    ackStore.updatedAt = now;
    const path = await saveAcksStore(ackStore);
    return { path, ack };
}
async function pruneStaleAcks(options = {}) {
    const nowMs = typeof options.nowMs === "number" && Number.isFinite(options.nowMs) ? options.nowMs : Date.now();
    const dryRun = options.dryRun === true;
    const ackStore = await loadAcksStore();
    const pruned = pruneStaleAcksFromStore(ackStore, nowMs);
    let path = exports.ACKS_PATH;
    let updatedAt = ackStore.updatedAt;
    if (!dryRun && pruned.removed > 0) {
        path = await saveAcksStore(pruned.store);
        updatedAt = pruned.store.updatedAt;
    }
    return {
        path,
        dryRun,
        before: pruned.before,
        removed: pruned.removed,
        after: pruned.after,
        removedItemIds: pruned.removedItemIds,
        updatedAt,
    };
}
async function previewStaleAcksPrune(options = {}) {
    const result = await pruneStaleAcks({
        dryRun: true,
        nowMs: options.nowMs,
    });
    return {
        path: result.path,
        dryRun: true,
        before: result.before,
        removed: result.removed,
        after: result.after,
        updatedAt: result.updatedAt,
    };
}
function pruneStaleAcksFromStore(input, nowMs = Date.now()) {
    const normalized = normalizeAcksStore(input);
    const nextAcks = [];
    const removedItemIds = [];
    for (const ack of normalized.acks) {
        if (isAckExpired(ack, nowMs)) {
            removedItemIds.push(ack.itemId);
        }
        else {
            nextAcks.push(ack);
        }
    }
    const store = {
        acks: nextAcks,
        updatedAt: removedItemIds.length > 0 ? new Date(nowMs).toISOString() : normalized.updatedAt,
    };
    return {
        store,
        before: normalized.acks.length,
        removed: removedItemIds.length,
        after: nextAcks.length,
        removedItemIds,
    };
}
function validateAcknowledgeInput(input) {
    const obj = asObject(input);
    if (!obj) {
        throw new NotificationCenterValidationError("ack payload must be a JSON object.", [], 400);
    }
    const issues = [];
    const itemId = requiredString(obj.itemId, "itemId", 260, issues);
    const note = optionalString(obj.note, "note", 300, issues);
    const ttlMinutes = optionalPositiveInt(obj.ttlMinutes, "ttlMinutes", 1, 7 * 24 * 60, issues);
    const snoozeUntil = optionalIsoString(obj.snoozeUntil, "snoozeUntil", issues);
    if (ttlMinutes !== undefined && snoozeUntil !== undefined) {
        issues.push("Provide either ttlMinutes or snoozeUntil, not both");
    }
    if (snoozeUntil !== undefined && Date.parse(snoozeUntil) <= Date.now()) {
        issues.push("snoozeUntil must be a future ISO timestamp");
    }
    if (issues.length > 0) {
        throw new NotificationCenterValidationError("Invalid acknowledge payload.", issues, 400);
    }
    return { itemId, note, ttlMinutes, snoozeUntil };
}
function normalizeAcksStore(input) {
    const obj = asObject(input);
    if (!obj)
        return cloneEmptyAcks();
    return {
        acks: normalizeAcks(obj.acks),
        updatedAt: asIsoString(obj.updatedAt),
    };
}
function normalizeAcks(input) {
    if (!Array.isArray(input))
        return [];
    const unique = new Map();
    for (const item of input) {
        const obj = asObject(item);
        if (!obj)
            continue;
        const itemId = asString(obj.itemId)?.trim();
        if (!itemId)
            continue;
        unique.set(itemId, {
            itemId,
            ackedAt: asIsoString(obj.ackedAt),
            note: asString(obj.note)?.trim() || undefined,
            expiresAt: asIsoStringOptional(obj.expiresAt),
        });
    }
    return [...unique.values()].sort((a, b) => a.itemId.localeCompare(b.itemId));
}
function requiredString(input, label, maxLength, issues) {
    if (typeof input !== "string" || input.trim() === "") {
        issues.push(`${label} must be a non-empty string`);
        return "";
    }
    const trimmed = input.trim();
    if (trimmed.length > maxLength) {
        issues.push(`${label} must be <= ${maxLength} characters`);
    }
    return trimmed;
}
function optionalString(input, label, maxLength, issues) {
    if (input === undefined)
        return undefined;
    if (typeof input !== "string") {
        issues.push(`${label} must be a string`);
        return undefined;
    }
    const trimmed = input.trim();
    if (!trimmed)
        return undefined;
    if (trimmed.length > maxLength) {
        issues.push(`${label} must be <= ${maxLength} characters`);
        return undefined;
    }
    return trimmed;
}
function optionalPositiveInt(input, label, min, max, issues) {
    if (input === undefined)
        return undefined;
    if (typeof input !== "number" || !Number.isInteger(input)) {
        issues.push(`${label} must be an integer`);
        return undefined;
    }
    if (input < min || input > max) {
        issues.push(`${label} must be in range ${min}..${max}`);
        return undefined;
    }
    return input;
}
function optionalIsoString(input, label, issues) {
    if (input === undefined)
        return undefined;
    if (typeof input !== "string" || input.trim() === "") {
        issues.push(`${label} must be a non-empty ISO timestamp string`);
        return undefined;
    }
    const parsed = Date.parse(input);
    if (Number.isNaN(parsed)) {
        issues.push(`${label} must be a valid ISO timestamp`);
        return undefined;
    }
    return new Date(parsed).toISOString();
}
function cloneEmptyAcks() {
    return {
        acks: [],
        updatedAt: EMPTY_ACKS.updatedAt,
    };
}
function asObject(v) {
    return v !== null && typeof v === "object" && !Array.isArray(v) ? v : undefined;
}
function asString(v) {
    return typeof v === "string" ? v : undefined;
}
function asIsoString(v) {
    if (typeof v === "string" && !Number.isNaN(Date.parse(v)))
        return new Date(v).toISOString();
    return new Date().toISOString();
}
function asIsoStringOptional(v) {
    if (typeof v !== "string" || Number.isNaN(Date.parse(v)))
        return undefined;
    return new Date(v).toISOString();
}
function resolveAckExpiresAt(input, nowMs) {
    if (input.snoozeUntil)
        return input.snoozeUntil;
    if (typeof input.ttlMinutes === "number") {
        return new Date(nowMs + input.ttlMinutes * 60_000).toISOString();
    }
    return undefined;
}
function isAckExpired(ack, nowMs) {
    const expiresMs = typeof ack.expiresAt === "string" ? Date.parse(ack.expiresAt) : NaN;
    return Number.isFinite(expiresMs) && expiresMs <= nowMs;
}
function resolveActiveAck(ack, nowMs) {
    if (!ack)
        return undefined;
    if (isAckExpired(ack, nowMs))
        return undefined;
    return ack;
}
