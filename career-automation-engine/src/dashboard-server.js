const express = require('express');
const cors = require('cors');
const path = require('path');
const config = require('./lib/config');
const logger = require('./lib/logger');
const state = require('./lib/state');
const sheets = require('./lib/sheets');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'dashboard')));

app.get('/api/status', (req, res) => {
  res.json(state.read());
});

app.post('/api/approve', (req, res) => {
  const current = state.read();
  if (current.status !== 'FORM_FILLED') {
    return res.status(409).json({ success: false, message: 'No application is currently awaiting approval.' });
  }
  // job-processor.js (which owns the live browser page) is the one
  // watching for this flag and will do the actual submit + confirmation
  // capture; this endpoint can't touch the page directly since it runs
  // in a different process.
  state.write({ status: 'APPROVED', job: current.job });
  logger.info(`Approved by Nathan: ${current.job.company} | ${current.job.role}`);
  res.json({ success: true, message: 'Approved — submitting now.' });
});

app.post('/api/reject', (req, res) => {
  const current = state.read();
  if (current.status !== 'FORM_FILLED') {
    return res.status(409).json({ success: false, message: 'No application is currently awaiting approval.' });
  }
  state.write({ status: 'REJECTED', job: current.job });
  logger.info(`Rejected by Nathan: ${current.job.company} | ${current.job.role}`);
  res.json({ success: true, message: 'Rejected — moving to next job.' });
});

app.get('/api/log', async (req, res) => {
  try {
    const jobs = await sheets.readAllJobs();
    const recent = jobs
      .filter((j) => j.status === 'SUBMITTED' || j.status === 'REJECTED')
      .slice(-5)
      .reverse();
    res.json(recent);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(config.automation.dashboardPort, () => {
  console.log('🚀 CAREER AUTOMATION DASHBOARD');
  console.log(`Open: http://localhost:${config.automation.dashboardPort}`);
  logger.info(`Dashboard listening on port ${config.automation.dashboardPort}`);
});
