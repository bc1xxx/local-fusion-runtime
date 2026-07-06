# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Local Fusion Runtime, please report it privately.

**Do not** open a public issue. Instead, email the maintainers or open a draft security advisory on GitHub.

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

## Response

We will acknowledge receipt within 48 hours and aim to release a fix within 7 days.

## Scope

This project runs entirely locally and makes no network calls except to the local Ollama API.
Vulnerabilities are most likely in:
- Dependency supply chain
- Prompt injection through the API
- Command injection via model names (not applicable — models are configured in code)

## Responsible Disclosure

We ask that you give us reasonable time to fix a vulnerability before disclosing it publicly.
