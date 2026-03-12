"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createToolClient = createToolClient;
const openclaw_live_client_1 = require("./openclaw-live-client");
function createToolClient() {
    return new openclaw_live_client_1.OpenClawLiveClient();
}
