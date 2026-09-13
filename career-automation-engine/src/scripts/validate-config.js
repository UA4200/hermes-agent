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
  check('NOTION_API_KEY configured', !!config.notion.apiKey, 'set NOTION_API_KEY in .env — see SETUP.md');
  check('NOTION_DATA_SOURCE_ID configured', !!config.notion.dataSourceId, 'set NOTION_DATA_SOURCE_ID in .env');
  check(
    'INDEED_SESSION_COOKIE configured',
    !!config.indeed.sessionCookie,
    'set INDEED_SESSION_COOKIE in .env (see SETUP.md)'
  );
  check('RESUME_PATH points to a real file', fs.existsSync(config.applicant.resumePath), config.applicant.resumePath);
  check('APPLICANT_EMAIL configured', !!config.applicant.email);

  if (config.notion.apiKey && config.notion.dataSourceId) {
    try {
      const notion = require('../lib/notion');
      await notion.readAllJobs();
      check('Notion connection', true);
    } catch (err) {
      check('Notion connection', false, `${err.message} — is the database shared with your integration? (SETUP.md step 2)`);
    }
  }

  console.log(ok ? '\nAll checks pass.' : '\nSome checks failed — fix the above before running Phase 2+.');
  process.exit(ok ? 0 : 1);
}

main();
