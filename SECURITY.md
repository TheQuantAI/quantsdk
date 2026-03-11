# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to **security@thequantai.in**.

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include as much of the following information as possible:

- Type of issue (e.g., credential exposure, dependency vulnerability, code injection)
- Full paths of source file(s) related to the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## What to Expect

1. **Acknowledgement** — We will acknowledge receipt of your report within 48 hours.
2. **Assessment** — We will assess the vulnerability and determine its impact within 5 business days.
3. **Fix** — We will work on a fix and coordinate disclosure with you.
4. **Disclosure** — We will publish a security advisory once the fix is released.

## Scope

The following are in scope:

- QuantSDK Python package (`src/quantsdk/`)
- Backend credential handling (IBM API tokens, etc.)
- Dependency supply chain vulnerabilities
- OpenQASM parsing vulnerabilities (code injection via malicious QASM)
- CI/CD pipeline security

The following are out of scope:

- Vulnerabilities in upstream dependencies (Qiskit, NumPy, etc.) — report those to the respective projects
- Issues in the documentation site itself (unless they lead to code execution)

## Safe Harbor

We support safe harbor for security researchers who:

- Make a good faith effort to avoid privacy violations, destruction of data, and interruption or degradation of our services
- Only interact with accounts you own or with explicit permission of the account holder
- Do not exploit a security issue you discover for any reason other than reporting

## Recognition

We appreciate responsible disclosure and will acknowledge security researchers in our release notes (unless you prefer to remain anonymous).
