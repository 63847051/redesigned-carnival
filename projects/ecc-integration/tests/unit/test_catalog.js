import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CLAW_DIR = path.join(__dirname, '../../.claw');
const DATA_DIR = path.join(__dirname, '../../data');

describe('Catalog Generator', () => {
    it('should generate catalog files', () => {
        const jsonPath = path.join(DATA_DIR, 'claw-catalog.json');
        const mdPath = path.join(DATA_DIR, 'claw-catalog.md');

        assert(fs.existsSync(jsonPath), 'JSON catalog should exist');
        assert(fs.existsSync(mdPath), 'Markdown catalog should exist');
    });

    it('should have valid JSON structure', () => {
        const jsonPath = path.join(DATA_DIR, 'claw-catalog.json');
        const content = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));

        assert.ok(content.generated, 'should have generated timestamp');
        assert.ok(content.agents !== undefined, 'should have agents array');
        assert.ok(content.skills !== undefined, 'should have skills array');
        assert.ok(content.commands !== undefined, 'should have commands array');
        assert.ok(content.summary !== undefined, 'should have summary');
    });

    it('should have correct summary counts', () => {
        const jsonPath = path.join(DATA_DIR, 'claw-catalog.json');
        const content = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));

        const total = content.summary.agents + content.summary.skills +
                     content.summary.commands + content.summary.hooks +
                     content.summary.rules;

        assert.strictEqual(total, content.summary.total, 'summary total should match sum');
    });

    it('.claw directories should exist', () => {
        assert(fs.existsSync(path.join(CLAW_DIR, 'agents')), 'agents dir should exist');
        assert(fs.existsSync(path.join(CLAW_DIR, 'skills')), 'skills dir should exist');
        assert(fs.existsSync(path.join(CLAW_DIR, 'commands')), 'commands dir should exist');
        assert(fs.existsSync(path.join(CLAW_DIR, 'hooks')), 'hooks dir should exist');
        assert(fs.existsSync(path.join(CLAW_DIR, 'rules')), 'rules dir should exist');
    });
});