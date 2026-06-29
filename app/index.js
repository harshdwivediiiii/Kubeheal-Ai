const express = require('express');
const os = require('os');

const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({
    status: 'ok',
    message: 'KubeHeal AI — app is running',
    hostname: os.hostname(),
    uptime: process.uptime(),
  });
});

app.get('/healthz', (req, res) => {
  res.status(200).json({ health: 'alive' });
});

app.get('/crash', (req, res) => {
  // Phase 3: intentional crash endpoint
  console.error('[kubeheal-app] CRASH: intentional crash triggered via /crash endpoint. process.exit(1)');
  res.status(500).json({ error: 'intentional crash triggered' });
  process.exit(1);
});

app.listen(PORT, () => {
  console.log(`[kubeheal-app] listening on port ${PORT}`);
});
