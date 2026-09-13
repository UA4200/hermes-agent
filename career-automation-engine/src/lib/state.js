// File-based state shared between dashboard-server.js and job-processor.js.
//
// The original spec's pseudocode had both processes reading/writing a
// plain in-memory `let currentJob` variable — that only works if they're
// the same process. Since SETUP.md runs them as two separate `node`
// processes (Terminal 1 / Terminal 2), state has to live outside either
// process. A small JSON file is the simplest thing that actually works
// for a single-user, single-machine tool like this.
const fs = require('fs');
const config = require('./config');

const IDLE = { status: 'IDLE', job: null };

function read() {
  try {
    return JSON.parse(fs.readFileSync(config.stateFile, 'utf8'));
  } catch {
    return IDLE;
  }
}

function write(state) {
  fs.mkdirSync(require('path').dirname(config.stateFile), { recursive: true });
  fs.writeFileSync(config.stateFile, JSON.stringify(state, null, 2));
}

module.exports = { read, write, IDLE };
