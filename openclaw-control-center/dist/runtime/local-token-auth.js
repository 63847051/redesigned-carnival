"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.evaluateLocalTokenGate = evaluateLocalTokenGate;
exports.normalizeToken = normalizeToken;
exports.readAuthorizationBearer = readAuthorizationBearer;
function evaluateLocalTokenGate(input) {
    if (!input.gateRequired) {
        return {
            ok: true,
            statusCode: 200,
            message: "Local token auth gate disabled.",
        };
    }
    const expected = normalizeToken(input.configuredToken);
    if (!expected) {
        return {
            ok: false,
            statusCode: 403,
            message: `Local token auth gate blocked ${input.routeLabel}. Set LOCAL_API_TOKEN to explicitly allow protected operations.`,
        };
    }
    const provided = normalizeToken(input.providedToken);
    if (!provided) {
        return {
            ok: false,
            statusCode: 401,
            message: `Missing local token for ${input.routeLabel}. Provide 'x-local-token' header or 'Authorization: Bearer <token>'.`,
        };
    }
    if (provided !== expected) {
        return {
            ok: false,
            statusCode: 403,
            message: `Invalid local token for ${input.routeLabel}.`,
        };
    }
    return {
        ok: true,
        statusCode: 200,
        message: "Local token authorized.",
    };
}
function normalizeToken(value) {
    if (typeof value !== "string")
        return undefined;
    const trimmed = value.trim();
    if (!trimmed)
        return undefined;
    if (trimmed.length > 256)
        return undefined;
    if (/[\u0000-\u001F\u007F]/.test(trimmed))
        return undefined;
    return trimmed;
}
function readAuthorizationBearer(value) {
    if (!value)
        return undefined;
    const match = value.match(/^Bearer\s+(.+)$/i);
    return match?.[1];
}
