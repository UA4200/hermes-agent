require('dotenv').config();
const path = require('path');

function required(name, fallback = undefined) {
  const v = process.env[name] ?? fallback;
  return v;
}

const config = {
  claude: {
    apiKey: required('CLAUDE_API_KEY'),
    model: required('CLAUDE_MODEL', 'claude-opus-5'),
    batchSize: Number(required('CLAUDE_BATCH_SIZE', '10')),
    fitThreshold: Number(required('FIT_THRESHOLD', '70')),
  },
  google: {
    sheetId: required('GOOGLE_SHEET_ID'),
    serviceAccountKeyPath: path.resolve(
      process.cwd(),
      required('GOOGLE_SERVICE_ACCOUNT_KEY_PATH', './service-account.json')
    ),
  },
  indeed: {
    sessionCookie: required('INDEED_SESSION_COOKIE'),
    accountEmail: required('INDEED_ACCOUNT_EMAIL'),
  },
  linkedin: {
    sessionCookie: required('LINKEDIN_SESSION_COOKIE'),
  },
  applicant: {
    firstName: required('APPLICANT_FIRST_NAME'),
    lastName: required('APPLICANT_LAST_NAME'),
    email: required('APPLICANT_EMAIL'),
    phone: required('APPLICANT_PHONE'),
    resumePath: required('RESUME_PATH', './resume.pdf'),
  },
  automation: {
    dashboardPort: Number(required('DASHBOARD_PORT', '3000')),
    headless: required('HEADLESS_BROWSER', 'true') !== 'false',
    screenshotOnError: required('SCREENSHOT_ON_ERROR', 'true') !== 'false',
    screenshotDir: path.resolve(process.cwd(), required('SCREENSHOT_DIR', './screenshots')),
  },
  logging: {
    level: required('LOG_LEVEL', 'INFO'),
    dir: path.resolve(process.cwd(), required('LOG_DIR', './logs')),
  },
  stateFile: path.resolve(process.cwd(), 'state/current-job.json'),
};

module.exports = config;
