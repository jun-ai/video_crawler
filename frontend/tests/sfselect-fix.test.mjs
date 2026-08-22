import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
// Test file lives at /root/video_crawler/frontend/tests/
// So repo root is two levels up from tests/
const REPO_ROOT = join(__dirname, '..', '..');

const PAGES = [
  'frontend/src/views/admin/MaterialsManage.vue',
  'frontend/src/views/admin/upload/Transcribe.vue',
  'frontend/src/views/admin/upload/FetchFromUrl.vue',
  'frontend/src/views/admin/TagsManage.vue',
  'frontend/src/views/admin/MaterialUpload.vue',
];

test('SfSelect fix: no empty/null value in 5 admin pages', () => {
  const violations = [];
  for (const rel of PAGES) {
    const path = join(REPO_ROOT, rel);
    if (!existsSync(path)) {
      violations.push(`${rel}: FILE MISSING`);
      continue;
    }
    const content = readFileSync(path, 'utf8');
    if (/value:\s*''/g.test(content)) {
      violations.push(`${rel}: contains value: ''`);
    }
    if (/value:\s*null\b/g.test(content)) {
      violations.push(`${rel}: contains value: null`);
    }
  }
  assert.deepEqual(violations, [], `SfSelect options violations:\n${violations.join('\n')}`);
});

test('MaterialsManage.vue: 3 "all" sentinels (category/status/duration)', () => {
  const path = join(REPO_ROOT, 'frontend/src/views/admin/MaterialsManage.vue');
  const content = readFileSync(path, 'utf8');
  const count = (content.match(/value:\s*'all'/g) || []).length;
  assert.ok(count >= 3, `expected >=3 'all' sentinel, found ${count}`);
});

test('Transcribe.vue: "auto" sentinel + submitTranscribe guard', () => {
  const path = join(REPO_ROOT, 'frontend/src/views/admin/upload/Transcribe.vue');
  const content = readFileSync(path, 'utf8');
  assert.match(content, /value:\s*'auto'/, 'Transcribe should use auto sentinel');
  assert.match(content, /form\.value\.language\s*!==\s*'auto'/, 'submitTranscribe should skip auto sentinel');
});

test('loadMaterials converts "all" sentinel to undefined for backend', () => {
  const path = join(REPO_ROOT, 'frontend/src/views/admin/MaterialsManage.vue');
  const content = readFileSync(path, 'utf8');
  const transforms = (content.match(/===\s*'all'\s*\?\s*undefined/g) || []).length;
  assert.ok(transforms >= 3, `expected >=3 'all' -> undefined transforms, found ${transforms}`);
});

test('dist/ has MaterialsManage + SfSelect + Transcribe bundles', () => {
  const assets = join(REPO_ROOT, 'frontend/dist/assets');
  if (!existsSync(assets)) {
    console.log('  (skip: dist not built)');
    return;
  }
  const files = readdirSync(assets);
  const mm = files.find(f => f.startsWith('MaterialsManage-') && f.endsWith('.js'));
  const sf = files.find(f => f.startsWith('SfSelect-') && f.endsWith('.js'));
  const tr = files.find(f => f.startsWith('Transcribe-') && f.endsWith('.js'));
  assert.ok(mm, 'MaterialsManage bundle missing');
  assert.ok(sf, 'SfSelect bundle missing');
  assert.ok(tr, 'Transcribe bundle missing');
  console.log(`  bundles: ${mm}, ${sf}, ${tr}`);
});