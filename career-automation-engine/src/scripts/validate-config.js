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
  check(
    'INDEED_SESSION_COOKIE configured',
    !!config.indeed.sessionCookie,
    'set INDEED_SESSION_COOKIE in .env (see SETUP.md)'
  );
  check('RESUME_PATH points to a real file', fs.existsSync(config.applicant.resumePath), config.applicant.resumePath);
  check('APPLICANT_EMAIL configured', !!config.applicant.email);

  try {
    const tracker = require('../lib/tracker');
    await tracker.readAllJobs();
    check('Tracker file readable/writable', true, config.tracker.path);
  } catch (err) {
    check('Tracker file readable/writable', false, `${err.message} — check TRACKER_PATH and that its parent folder exists`);
  }

  console.log(ok ? '\nAll checks pass.' : '\nSome checks failed — fix the above before running Phase 2+.');
  process.exit(ok ? 0 : 1);
}

main();
