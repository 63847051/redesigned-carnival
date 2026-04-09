const fs = require('fs');
const path = require('path');

const LOG_DIR = path.join(__dirname, '../../../logs');
const SESSION_LOG = path.join(LOG_DIR, 'session.log');

function ensureDir(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}

function log(message) {
    ensureDir(LOG_DIR);
    const timestamp = new Date().toISOString();
    const logLine = `[${timestamp}] ${message}\n`;
    fs.appendFileSync(SESSION_LOG, logLine);
}

function sessionStart(context) {
    const sessionId = context.sessionId || `session-${Date.now()}`;
    const userId = context.userId || 'unknown';

    log(`SESSION_START: session=${sessionId} user=${userId}`);

    console.log(`🔔 Session started: ${sessionId}`);

    return {
        sessionId,
        startedAt: new Date().toISOString(),
        status: 'initialized'
    };
}

if (require.main === module) {
    const mockContext = {
        sessionId: 'test-session-001',
        userId: 'test-user'
    };
    const result = sessionStart(mockContext);
    console.log('Result:', result);
}

module.exports = { sessionStart, log };