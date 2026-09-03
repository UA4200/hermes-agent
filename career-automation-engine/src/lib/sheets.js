// Google Sheets tracker access, via a service account (not a bare API
// key — API keys are read-only for public sheets and cannot write rows,
// which every status update this system makes needs to do).
const { google } = require('googleapis');
const fs = require('fs');
const config = require('./config');

const COLUMNS = [
  'company', 'role', 'source', 'url', 'posted', 'salary',
  'fitScore', 'resumeUsed', 'formType', 'status',
  'submittedDate', 'confirmationCode', 'nextAction',
]; // A..M, matches tracking/sheets-schema.json

const SHEET_RANGE = 'Sheet1!A:M';

let sheetsClient = null;
async function getClient() {
  if (sheetsClient) return sheetsClient;
  if (!fs.existsSync(config.google.serviceAccountKeyPath)) {
    throw new Error(
      `Google service account key not found at ${config.google.serviceAccountKeyPath}. ` +
      `See SETUP.md step 2.`
    );
  }
  const auth = new google.auth.GoogleAuth({
    keyFile: config.google.serviceAccountKeyPath,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });
  sheetsClient = google.sheets({ version: 'v4', auth: await auth.getClient() });
  return sheetsClient;
}

function rowToObject(row) {
  const obj = {};
  COLUMNS.forEach((key, i) => { obj[key] = row[i] ?? ''; });
  return obj;
}

function objectToRow(obj) {
  return COLUMNS.map((key) => obj[key] ?? '');
}

/** Returns [{ rowNumber, ...fields }] for every data row (1-indexed, header excluded). */
async function readAllJobs() {
  const sheets = await getClient();
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId: config.google.sheetId,
    range: SHEET_RANGE,
  });
  const rows = res.data.values || [];
  const [, ...dataRows] = rows; // skip header
  return dataRows.map((row, i) => ({ rowNumber: i + 2, ...rowToObject(row) }));
}

async function findJobsByStatus(status, minScore = 0) {
  const jobs = await readAllJobs();
  return jobs
    .filter((j) => j.status === status && Number(j.fitScore || 0) >= minScore)
    .sort((a, b) => Number(b.fitScore || 0) - Number(a.fitScore || 0));
}

/** Appends new job rows (status defaults to SCORED if not set). */
async function appendJobs(jobs) {
  const sheets = await getClient();
  const values = jobs.map((j) => objectToRow({ status: 'SCORED', ...j }));
  await sheets.spreadsheets.values.append({
    spreadsheetId: config.google.sheetId,
    range: SHEET_RANGE,
    valueInputOption: 'USER_ENTERED',
    requestBody: { values },
  });
}

/** Patches specific columns on one row by its 1-indexed sheet row number. */
async function updateJobRow(rowNumber, fields) {
  const sheets = await getClient();
  const updates = Object.entries(fields).map(([key, value]) => {
    const colIndex = COLUMNS.indexOf(key);
    if (colIndex === -1) throw new Error(`Unknown tracker column: ${key}`);
    const colLetter = String.fromCharCode('A'.charCodeAt(0) + colIndex);
    return { range: `Sheet1!${colLetter}${rowNumber}`, values: [[value]] };
  });
  await sheets.spreadsheets.values.batchUpdate({
    spreadsheetId: config.google.sheetId,
    requestBody: { valueInputOption: 'USER_ENTERED', data: updates },
  });
}

async function findJobByUrl(url) {
  const jobs = await readAllJobs();
  return jobs.find((j) => j.url === url) || null;
}

module.exports = { readAllJobs, findJobsByStatus, appendJobs, updateJobRow, findJobByUrl, COLUMNS };
