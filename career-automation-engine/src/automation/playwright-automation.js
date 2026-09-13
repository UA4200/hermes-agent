// Form field detection + auto-fill. Best-effort and heuristic: real ATS
// forms vary too much to guarantee a fixed accuracy number, so this
// tries a set of common selector patterns per field and reports which
// fields it could NOT confidently fill, rather than claiming success it
// hasn't verified.
const path = require('path');
const logger = require('../lib/logger');

// Hints used only to choose a friendlier "formType" label for the tracker
// and to nudge field-matching order; the fill logic itself stays generic
// because scraping every ATS's real DOM structure isn't something that
// can be verified without live access to each one.
const ATS_HOSTNAME_HINTS = [
  { match: /myworkday\.com/, label: 'Workday' },
  { match: /greenhouse\.io/, label: 'Greenhouse' },
  { match: /lever\.co/, label: 'Lever' },
  { match: /indeed\.com/, label: 'Indeed' },
  { match: /linkedin\.com/, label: 'LinkedIn' },
];

function detectATS(page) {
  const host = new URL(page.url()).hostname;
  const hit = ATS_HOSTNAME_HINTS.find((h) => h.match.test(host));
  return hit ? hit.label : 'Unknown';
}

const FIELD_PATTERNS = {
  firstName: [/first.?name/i, /given.?name/i, /^fname$/i],
  lastName: [/last.?name/i, /family.?name/i, /surname/i, /^lname$/i],
  email: [/e-?mail/i],
  phone: [/phone/i, /mobile/i, /telephone/i],
  location: [/location/i, /city/i, /address/i],
};

async function findFieldByPatterns(page, patterns) {
  const candidates = await page.locator('input, textarea, select').all();
  for (const el of candidates) {
    const attrs = await el.evaluate((n) => ({
      name: n.getAttribute('name') || '',
      id: n.getAttribute('id') || '',
      placeholder: n.getAttribute('placeholder') || '',
      ariaLabel: n.getAttribute('aria-label') || '',
      type: n.getAttribute('type') || '',
    }));
    const haystack = `${attrs.name} ${attrs.id} ${attrs.placeholder} ${attrs.ariaLabel}`;
    if (attrs.type === 'hidden') continue;
    if (patterns.some((p) => p.test(haystack))) return el;
  }
  return null;
}

async function findResumeUpload(page) {
  const fileInputs = await page.locator('input[type="file"]').all();
  return fileInputs[0] || null;
}

/**
 * Fills whatever standard fields it can confidently identify.
 * Returns { filled: string[], missed: string[] } so the caller can decide
 * whether to pause for review before submitting.
 */
async function fillApplicationForm(page, applicant) {
  const filled = [];
  const missed = [];

  const textFields = {
    firstName: applicant.firstName,
    lastName: applicant.lastName,
    email: applicant.email,
    phone: applicant.phone,
    location: applicant.location,
  };

  for (const [field, value] of Object.entries(textFields)) {
    if (!value) continue;
    try {
      const el = await findFieldByPatterns(page, FIELD_PATTERNS[field]);
      if (el) {
        await el.fill(String(value));
        filled.push(field);
      } else {
        missed.push(field);
      }
    } catch (err) {
      logger.warn(`Field fill failed for ${field}: ${err.message}`);
      missed.push(field);
    }
  }

  if (applicant.resumePath) {
    try {
      const el = await findResumeUpload(page);
      if (el) {
        await el.setInputFiles(path.resolve(applicant.resumePath));
        filled.push('resume');
      } else {
        missed.push('resume');
      }
    } catch (err) {
      logger.warn(`Resume upload failed: ${err.message}`);
      missed.push('resume');
    }
  }

  return { filled, missed };
}

/**
 * Heuristic: anything that isn't one of the standard fields above and
 * looks like a question (textarea, radio group, select with >2 options)
 * counts as a "screening question" worth a human's eyes before submit.
 */
async function detectScreeningQuestions(page) {
  const textareas = await page.locator('textarea').count();
  const radioGroups = await page.locator('input[type="radio"]').count();
  const selects = await page.locator('select').count();
  return textareas + radioGroups + selects;
}

async function screenshotForReview(page, screenshotDir, jobId) {
  const fs = require('fs');
  fs.mkdirSync(screenshotDir, { recursive: true });
  const filePath = path.join(screenshotDir, `${jobId}_review.png`);
  await page.screenshot({ path: filePath, fullPage: true });
  return filePath;
}

async function screenshotOnError(page, screenshotDir, jobId, error) {
  const fs = require('fs');
  fs.mkdirSync(screenshotDir, { recursive: true });
  const filePath = path.join(screenshotDir, `${jobId}_error.png`);
  try {
    await page.screenshot({ path: filePath, fullPage: true });
  } catch { /* page may already be closed */ }
  logger.error(`${jobId}: ${error.message} (screenshot: ${filePath})`);
  return filePath;
}

/** Clicks the most likely submit button. Caller must already have approval. */
async function submitForm(page) {
  const submitButton = page
    .locator('button:has-text("Submit"), input[type="submit"], button[type="submit"]')
    .first();
  await submitButton.click();
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
}

/** Best-effort confirmation text scrape; returns null if nothing matched. */
async function captureConfirmation(page) {
  const selectors = [
    '[class*=confirmation]', '[class*=success]', '[data-testid*=confirmation]',
  ];
  for (const sel of selectors) {
    const el = page.locator(sel).first();
    if (await el.count()) {
      const text = (await el.textContent())?.trim();
      if (text) return text;
    }
  }
  return null;
}

module.exports = {
  detectATS,
  fillApplicationForm,
  detectScreeningQuestions,
  screenshotForReview,
  screenshotOnError,
  submitForm,
  captureConfirmation,
};
