// CSV tracker — replaces the earlier Notion database backend. A plain
// file needs no account, no API key, no sharing step: point TRACKER_PATH
// (.env) at a folder Google Drive for Desktop already syncs and the
// tracker shows up in Drive/your phone automatically, with zero API
// code. Defaults to a local file in this project if TRACKER_PATH isn't
// set, so the pipeline still works before you've wired up Drive at all.
//
// Single-user, low-frequency writes (one job at a time, human-paced
// approvals) — a whole-file read/rewrite per update is simple and
// correct for that; no need for row-level locking or a real database.
const fs = require('fs');
const path = require('path');
const config = require('./config');

const FIELDS = [
  'id', 'company', 'role', 'source', 'url', 'posted', 'salary',
  'fitScore', 'resumeUsed', 'formType', 'status',
  'submittedDate', 'confirmationCode', 'nextAction',
];

function csvEscape(value) {
  const s = String(value ?? '');
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

// Parses the whole file as one character stream rather than splitting
// into lines first — a quoted field containing a literal newline is
// valid CSV but isn't a row boundary, so row boundaries can only be
// found by tracking quote state across the whole text.
function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = '';
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') { inQuotes = false; }
      else { field += c; }
    } else if (c === '"') {
      inQuotes = true;
    } else if (c === ',') {
      row.push(field);
      field = '';
    } else if (c === '\n' || (c === '\r' && text[i + 1] === '\n')) {
      if (c === '\r') i++;
      row.push(field);
      field = '';
      rows.push(row);
      row = [];
    } else {
      field += c;
    }
  }
  if (field !== '' || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows.filter((r) => !(r.length === 1 && r[0] === ''));
}

function ensureFile() {
  const p = config.tracker.path;
  fs.mkdirSync(path.dirname(p), { recursive: true });
  if (!fs.existsSync(p)) {
    fs.writeFileSync(p, FIELDS.map(csvEscape).join(',') + '\n');
  }
}

function readRows() {
  ensureFile();
  const text = fs.readFileSync(config.tracker.path, 'utf8');
  const [, ...dataRows] = parseCsv(text); // skip header — column order is fixed by FIELDS
  return dataRows.map((values) => {
    const row = {};
    FIELDS.forEach((f, i) => { row[f] = values[i] ?? ''; });
    return row;
  });
}

function writeRows(rows) {
  const lines = [FIELDS.map(csvEscape).join(',')];
  for (const row of rows) {
    lines.push(FIELDS.map((f) => csvEscape(row[f])).join(','));
  }
  fs.writeFileSync(config.tracker.path, lines.join('\n') + '\n');
}

async function readAllJobs() {
  return readRows();
}

async function findJobsByStatus(status, minScore = 0) {
  const jobs = readRows();
  return jobs
    .filter((j) => j.status === status && Number(j.fitScore || 0) >= minScore)
    .sort((a, b) => Number(b.fitScore || 0) - Number(a.fitScore || 0));
}

async function findJobByUrl(url) {
  return readRows().find((j) => j.url === url) || null;
}

/** Appends new tracker rows (status defaults to SCORED if not set). */
async function appendJobs(jobs) {
  const rows = readRows();
  for (const job of jobs) {
    rows.push({ id: String(Date.now()) + Math.random().toString(36).slice(2, 6), status: 'SCORED', ...job });
  }
  writeRows(rows);
}

/** Patches specific fields on one row by its id. */
async function updateJobRow(id, fields) {
  const rows = readRows();
  const row = rows.find((r) => r.id === id);
  if (!row) throw new Error(`No tracker row with id ${id}`);
  Object.assign(row, fields);
  writeRows(rows);
}

module.exports = { readAllJobs, findJobsByStatus, findJobByUrl, appendJobs, updateJobRow, FIELDS };
