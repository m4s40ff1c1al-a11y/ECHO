# Security design

- Owner password: PBKDF2-HMAC-SHA256 with 600,000 iterations and per-password random salt.
- Session: signed cookie, HTTP-only, same-site, HTTPS-only in production.
- Memory: Fernet authenticated encryption at rest; key supplied through hosting secrets.
- API keys: server environment only; never browser JavaScript or Git.
- Uploads: extension allowlist, size limit, random storage names, private directory.
- Web research: results are untrusted input; never execute returned code.
- Evolution: proposal-first; this build does not run model-generated code, alter permissions, or deploy updates.
- Backups: encrypted database and key backup must be handled separately.
- Production hardening still required before public launch: persistent encrypted storage, reverse-proxy HTTPS, account recovery, stronger CSRF/session review, dependency scanning, rate limiting at edge, backups, monitoring, and independent security review.
