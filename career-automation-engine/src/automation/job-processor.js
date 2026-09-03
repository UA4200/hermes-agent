// Runs as its own process ("Terminal 2"). Owns the live Playwright
// browser/page — dashboard-server.js never touches the page directly,
// it only flips state via state.js, which this loop polls.
const { chromium } = require('playwright');
const config = require('../lib/config');
const logger = require('../lib/logger');
const state = require('../lib/state');
const sheets = require('../lib/sheets');
const {
  detectATS, fillApplicationForm, detectScreeningQuestions,
  screenshotForReview, screenshotOnError, submitForm, captureConfirmation,
} = require('./playwright-automation');

const POLL_MS = 2000;

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

async function waitForDecision() {
  while (true) {
    const current = state.read();
    if (current.status === 'APPROVED' || current.status === 'REJECTED') return current.status;
    await sleep(POLL_MS);
  }
}

async function processJob(browser, job) {
  const jobId = job.rowNumber;
  logger.info(`Loading job ${jobId}: ${job.company} | ${job.role}`);

  const page = await browser.newPage();
  try {
    await page.goto(job.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  } catch (err) {
    await screenshotOnError(page, config.automation.screenshotDir, jobId, err);
    await sheets.updateJobRow(jobId, { status: 'ERROR', nextAction: `Navigation failed: ${err.message}` });
    await page.close();
    return;
  }

  const formType = detectATS(page);
  logger.info(`Detected ATS: ${formType}`);

  const { filled, missed } = await fillApplicationForm(page, config.applicant);
  logger.info(`Filled: ${filled.join(', ') || 'none'} | Missed: ${missed.join(', ') || 'none'}`);

  const questionCount = await detectScreeningQuestions(page);
  const screenshotPath = await screenshotForReview(page, config.automation.screenshotDir, jobId);
  if (questionCount > 4) {
    logger.info(`${questionCount} screening questions detected on job ${jobId} — screenshot saved for review.`);
  }

  await sheets.updateJobRow(jobId, {
    status: 'FORM_FILLED',
    formType,
    nextAction: missed.length ? `Review missed fields: ${missed.join(', ')}` : 'Ready for approval',
  });

  state.write({
    status: 'FORM_FILLED',
    job: {
      rowNumber: jobId, company: job.company, role: job.role, url: job.url,
      fitScore: job.fitScore, formType, filled, missed, questionCount, screenshotPath,
    },
  });

  logger.info(`AWAITING APPROVAL: ${job.company} | ${job.role}`);
  const decision = await waitForDecision();

  if (decision === 'APPROVED') {
    try {
      await submitForm(page);
      const confirmation = await captureConfirmation(page);
      await sheets.updateJobRow(jobId, {
        status: 'SUBMITTED',
        submittedDate: new Date().toISOString(),
        confirmationCode: confirmation || '(not captured — verify manually)',
      });
      logger.info(`SUBMITTED job ${jobId}${confirmation ? ` — confirmation: ${confirmation}` : ' — no confirmation text found, verify manually'}`);
    } catch (err) {
      await screenshotOnError(page, config.automation.screenshotDir, jobId, err);
      await sheets.updateJobRow(jobId, { status: 'ERROR', nextAction: `Submit failed: ${err.message}` });
    }
  } else {
    await sheets.updateJobRow(jobId, { status: 'REJECTED' });
    logger.info(`REJECTED job ${jobId} by Nathan's review.`);
  }

  state.write(state.IDLE);
  await page.close();
}

async function main() {
  logger.info('Loading jobs from tracker...');
  const jobs = await sheets.findJobsByStatus('SCORED', config.claude.fitThreshold);
  logger.info(`Filtering to ${config.claude.fitThreshold}+ score threshold: ${jobs.length} qualified`);

  if (jobs.length === 0) {
    logger.info('No qualified jobs found. Run `npm run score` first, then restart this process.');
    return;
  }

  const browser = await chromium.launch({ headless: config.automation.headless });
  try {
    for (const job of jobs) {
      await processJob(browser, job);
    }
  } finally {
    await browser.close();
  }
  logger.info('Queue exhausted. Run `npm run fetch && npm run score` to load more jobs, then restart.');
}

main().catch((err) => {
  logger.error(`Fatal: ${err.stack || err.message}`);
  process.exit(1);
});
