// Notion database tracker access — replaces the earlier Google Sheets
// backend. Uses the Notion REST API directly (Node 18+ has global
// fetch, so no extra dependency), against the 2025-09-03 data-source
// model: pages are queried/created against a data SOURCE id, not the
// database id itself (a database can hold multiple data sources; this
// one has exactly one, created for this project).
const config = require('./config');

const API = 'https://api.notion.com/v1';
const VERSION = '2025-09-03';

const PROP = {
  company: 'Company', role: 'Role', source: 'Source', url: 'URL',
  posted: 'Posted', salary: 'Salary', fitScore: 'Fit Score',
  resumeUsed: 'Resume Used', formType: 'Form Type', status: 'Status',
  submittedDate: 'Submitted Date', confirmationCode: 'Confirmation',
  nextAction: 'Next Action',
};
const TITLE_FIELD = 'company';
const SELECT_FIELDS = new Set(['source', 'formType', 'status']);
const URL_FIELDS = new Set(['url']);
const NUMBER_FIELDS = new Set(['fitScore']);

function headers() {
  if (!config.notion.apiKey) {
    throw new Error('NOTION_API_KEY not set — see SETUP.md.');
  }
  return {
    Authorization: `Bearer ${config.notion.apiKey}`,
    'Notion-Version': VERSION,
    'Content-Type': 'application/json',
  };
}

async function request(path, options = {}) {
  const res = await fetch(`${API}${path}`, { ...options, headers: headers() });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(`Notion API ${path} failed: ${res.status} ${body.message || JSON.stringify(body)}`);
  }
  return body;
}

function toPropertyValue(field, value) {
  if (field === TITLE_FIELD) {
    return { title: [{ text: { content: String(value ?? '').slice(0, 2000) } }] };
  }
  if (SELECT_FIELDS.has(field)) {
    return value ? { select: { name: String(value).slice(0, 100) } } : { select: null };
  }
  if (URL_FIELDS.has(field)) {
    return { url: value || null };
  }
  if (NUMBER_FIELDS.has(field)) {
    return { number: value === '' || value === undefined || value === null ? null : Number(value) };
  }
  return { rich_text: [{ text: { content: String(value ?? '').slice(0, 2000) } }] };
}

function fromPage(page) {
  const props = page.properties;
  const get = (field) => {
    const p = props[PROP[field]];
    if (!p) return '';
    if (p.type === 'title') return p.title.map((t) => t.plain_text).join('');
    if (p.type === 'rich_text') return p.rich_text.map((t) => t.plain_text).join('');
    if (p.type === 'select') return p.select ? p.select.name : '';
    if (p.type === 'url') return p.url || '';
    if (p.type === 'number') return p.number ?? '';
    return '';
  };
  const job = { pageId: page.id };
  for (const field of Object.keys(PROP)) job[field] = get(field);
  return job;
}

/** Returns every tracked job as a flat object with a Notion pageId. */
async function readAllJobs() {
  const jobs = [];
  let cursor;
  do {
    const body = await request(`/data_sources/${config.notion.dataSourceId}/query`, {
      method: 'POST',
      body: JSON.stringify(cursor ? { start_cursor: cursor } : {}),
    });
    jobs.push(...body.results.map(fromPage));
    cursor = body.has_more ? body.next_cursor : null;
  } while (cursor);
  return jobs;
}

async function findJobsByStatus(status, minScore = 0) {
  const jobs = await readAllJobs();
  return jobs
    .filter((j) => j.status === status && Number(j.fitScore || 0) >= minScore)
    .sort((a, b) => Number(b.fitScore || 0) - Number(a.fitScore || 0));
}

async function findJobByUrl(url) {
  const jobs = await readAllJobs();
  return jobs.find((j) => j.url === url) || null;
}

/** Creates new tracker rows (status defaults to SCORED if not set). */
async function appendJobs(jobs) {
  for (const job of jobs) {
    const full = { status: 'SCORED', ...job };
    const properties = {};
    for (const field of Object.keys(PROP)) {
      if (full[field] !== undefined) properties[PROP[field]] = toPropertyValue(field, full[field]);
    }
    await request('/pages', {
      method: 'POST',
      body: JSON.stringify({
        parent: { type: 'data_source_id', data_source_id: config.notion.dataSourceId },
        properties,
      }),
    });
  }
}

/** Patches specific fields on one row by its Notion page ID. */
async function updateJobRow(pageId, fields) {
  const properties = {};
  for (const [field, value] of Object.entries(fields)) {
    if (!PROP[field]) throw new Error(`Unknown tracker field: ${field}`);
    properties[PROP[field]] = toPropertyValue(field, value);
  }
  await request(`/pages/${pageId}`, { method: 'PATCH', body: JSON.stringify({ properties }) });
}

module.exports = { readAllJobs, findJobsByStatus, findJobByUrl, appendJobs, updateJobRow, PROP };
