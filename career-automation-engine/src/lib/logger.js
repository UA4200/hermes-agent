const fs = require('fs');
const path = require('path');
const config = require('./config');

fs.mkdirSync(config.logging.dir, { recursive: true });
const logPath = path.join(config.logging.dir, 'automation.log');

function write(level, msg) {
  const line = `[${new Date().toISOString()}] [${level}] ${msg}`;
  if (level === 'ERROR') console.error(line); else console.log(line);
  fs.appendFile(logPath, line + '\n', () => {});
}

module.exports = {
  info: (msg) => write('INFO', msg),
  error: (msg) => write('ERROR', msg),
  warn: (msg) => write('WARN', msg),
};
