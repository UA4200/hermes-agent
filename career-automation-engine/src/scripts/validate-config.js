const fs = require('fs');
const config = require('../lib/config');

let ok = true;
function check(label, pass, hint) {
  if (pass) {
    console.log(`✓ ${label}`);
  } else {
    ok = false;
    console.log(`✗ ${label}${hint ? ` — ${hint}` : ''}`);
  }
}

async function main() {
  check('CLAUDE_API_KEY configured', !!config.claude.apiKey, 'set CLAUDE_API_KEY in .env');
  check('GOOGLE_SHEET_ID configured', !!config.google.sheetId, 'set GOOGLE_SHEET_ID in .env');
  check(
    'Google service account key file present',
    fs.existsSync(config.google.serviceAccountKeyPath),
    `expected file at ${config.google.serviceAccountKeyPath} — see SETUP.md step 2`
  );
  check(
    'INDEED_SESSION_COOKIE configured',
    !!config.indeed.sessionCookie,
    'set INDEED_SESSION_COOKIE in .env (see SETUP.md)'
  );
  check('RESUME_PATH points to a real file', fs.existsSync(config.applicant.resumePath), config.applicant.resumePath);
  check('APPLICANT_EMAIL configured', !!config.applicant.email);

  if (config.google.sheetId && fs.existsSync(config.google.serviceAccountKeyPath)) {
    try {
      const sheets = require('../lib/sheets');
      await sheets.readAllJobs();
      check('Google Sheets connection', true);
    } catch (err) {
      check('Google Sheets connection', false, err.message);
    }
  }

  console.log(ok ? '\nAll checks pass.' : '\nSome checks failed — fix the above before running Phase 2+.');
  process.exit(ok ? 0 : 1);
}

main();
