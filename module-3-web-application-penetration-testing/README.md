# Module 3 — Web Application Penetration Testing

## OWASP Juice Shop & DVWA

This project was developed as part of **Cybersecurity Laboratories — Module 3** at the **University of Minho**.

The objective was to perform a structured **web application penetration test** against two intentionally vulnerable applications:

- **OWASP Juice Shop**
- **DVWA (Damn Vulnerable Web Application)** configured at **Medium** security level

The assessment was carried out entirely in a **controlled and isolated local environment**, with both targets running in Docker containers inside a **Kali Linux ARM64 virtual machine using UTM**.

The work followed the **Penetration Testing Execution Standard (PTES)** and was complemented by the **OWASP Web Security Testing Guide v4.2 (WSTG)**.

Across both phases, **17 security findings** were identified and actively validated. The assessment covered vulnerabilities including SQL Injection, Broken Access Control, authentication weaknesses, cryptographic failures, Cross-Site Scripting, Command Injection, unrestricted file upload, Local File Inclusion, CSRF and predictable session identifiers.

---

# 1. Objectives

The main goals of the assessment were to:

- Perform reconnaissance and endpoint discovery
- Identify web application vulnerabilities
- Validate vulnerabilities through controlled exploitation
- Evaluate the practical security impact of each finding
- Assign CVSS v4 severity scores
- Map findings to OWASP and MITRE ATT&CK
- Compare exploitation techniques across different web applications
- Evaluate the effectiveness of DVWA Medium security controls
- Produce technical Proofs of Concept
- Recommend appropriate mitigations

---

# 2. Scope

The penetration test was divided into two phases.

| Phase | Target | Environment |
|---|---|---|
| Phase A | OWASP Juice Shop | Docker / Kali Linux VM |
| Phase B | DVWA — Medium Security | Docker / Kali Linux VM |

The targets were hosted locally and were not exposed to external networks.

```text
macOS Host
   │
   ▼
UTM Virtual Machine
   │
   ▼
Kali Linux ARM64
   │
   ├── Docker
   │    ├── OWASP Juice Shop
   │    └── DVWA
   │
   └── Penetration Testing Toolkit
```

This environment ensured that all exploitation activity remained isolated from production systems.

---

# 3. Methodology

The assessment followed the **Penetration Testing Execution Standard (PTES)**.

## 3.1 Pre-Engagement

The scope and Rules of Engagement were defined before testing.

All tests were restricted to the local laboratory environment.

## 3.2 Intelligence Gathering

The applications were inspected to identify:

- Endpoints
- Parameters
- Authentication mechanisms
- Hidden directories
- API behavior
- Session handling
- Potential injection points

Tools such as Burp Suite, gobuster, ffuf, sqlmap and commix were used throughout this stage.

## 3.3 Threat Modeling

Potential attack vectors were prioritized based on:

- Exposure
- Exploitability
- Authentication requirements
- Potential confidentiality impact
- Potential integrity impact

## 3.4 Vulnerability Analysis

Potential vulnerabilities were manually and automatically tested.

Burp Suite was used extensively for:

- HTTP interception
- Request manipulation
- Response analysis
- Parameter testing
- Authentication testing
- Replaying requests
- Fuzzing and brute-force testing

## 3.5 Exploitation

Identified vulnerabilities were actively validated in the controlled environment.

Successful exploitation included:

- Authentication bypass
- Database extraction
- Credential recovery
- Access-control bypass
- JavaScript execution
- Remote command execution
- Webshell upload
- Sensitive file disclosure
- Session manipulation

## 3.6 Post-Exploitation & Impact Analysis

After exploitation, the practical impact of each vulnerability was assessed.

Examples included:

- Administrative account access
- Access to other users' data
- Database exfiltration
- Password hash recovery
- Session cookie exposure
- Remote operating-system command execution
- Reading sensitive server files

---

# 4. Toolkit

| Tool | Primary Use |
|---|---|
| **Burp Suite Community** | Proxy, HTTP History, Repeater, Intruder, Intercept, Decoder |
| **sqlmap** | SQL Injection detection and database extraction |
| **gobuster** | Directory and file enumeration |
| **ffuf** | Parameter fuzzing and resource discovery |
| **commix** | Command Injection detection and exploitation |
| **Firefox** | Target interaction through configured proxy |
| **Firefox DevTools** | HTTP inspection and session-cookie analysis |
| **Docker** | Target containerization and isolation |
| **Hydra** | Brute-force testing |
| **Medusa** | Brute-force testing |
| **Kali Linux** | Penetration-testing environment |
| **UTM** | ARM64 virtualization environment |

---

# 5. Phase A — OWASP Juice Shop

Phase A focused on OWASP Juice Shop.

Nine findings were documented.

## FIND-A-001 — SQL Injection Authentication Bypass

A SQL Injection vulnerability in the login functionality allowed authentication controls to be bypassed.

**Impact:**

- Authentication bypass
- Administrative access
- Unauthorized account access

**Severity:** Critical

---

## FIND-A-002 — Broken Access Control / IDOR

The shopping-basket endpoint did not correctly verify that the requested basket belonged to the authenticated user.

Manipulating a numeric resource identifier allowed access to another user's basket.

**Impact:**

- Unauthorized access to user data
- Broken object-level authorization

**Severity:** High

---

## FIND-A-003 — Cryptographic Failure in JWT

The authentication JWT exposed an MD5 password hash inside its Base64-encoded payload.

Because JWT payloads are not encrypted by default, the hash could be extracted and recovered using password-cracking resources.

**Impact:**

- Credential exposure
- Password recovery
- Account compromise

**Severity:** High

---

## FIND-A-004 — Missing Brute-Force Protection

The login endpoint did not implement sufficient protections against repeated authentication attempts.

Burp Suite Intruder was used with a password wordlist to test credentials.

**Missing controls included:**

- Rate limiting
- Account lockout
- CAPTCHA
- Multi-factor authentication

**Severity:** Critical

---

## FIND-A-005 — SQL Injection Database Extraction

A SQL Injection vulnerability was further exploited with **sqlmap**.

The vulnerable login parameter allowed the extraction of application database records.

The extracted information included:

- User email addresses
- Roles
- Password hashes
- Authentication-related information

**Severity:** Critical

---

## FIND-A-006 — Security Misconfiguration / Exposed FTP Directory

A publicly accessible `/ftp` directory exposed development and backup files.

Although some files were protected by extension filtering, the control could be bypassed using a Poison Null Byte technique.

**Impact:**

- Sensitive file disclosure
- Exposure of development artifacts
- Information leakage

**Severity:** High

---

## FIND-A-007 — Reflected Cross-Site Scripting

The application search functionality reflected user-controlled input without sufficient output sanitization.

This allowed arbitrary JavaScript execution in the victim's browser.

**Impact:**

- JavaScript execution
- Potential session theft
- Client-side actions performed in the victim's context

**Severity:** Medium

---

## FIND-A-008 — Broken Access Control via Parameter Pollution

Authorization controls could be bypassed through duplicated `BasketId` values.

The backend validated one value but used another when performing the operation.

**Impact:**

- Manipulation of another user's resources
- Authorization bypass
- Unauthorized data modification

**Severity:** High

---

## FIND-A-009 — Predictable Authentication Credentials

Client-side JavaScript exposed deterministic password-generation logic associated with the application's OAuth functionality.

The transformation was reversible, making generated credentials predictable.

**Impact:**

- Credential prediction
- Third-party account compromise
- Broken authentication

---

# 6. Phase B — DVWA Medium

Phase B tested the same penetration-testing methodology against **DVWA configured at Medium security level**.

The objective was not only to identify vulnerabilities, but also to determine whether the additional controls could be bypassed.

Eight findings were documented.

---

## FIND-B-001 — Missing Brute-Force Protection

The DVWA brute-force module allowed unlimited authentication attempts.

Burp Suite Intruder was used with the `rockyou.txt` wordlist.

Unlike Juice Shop, the endpoint returned HTTP 200 for both successful and unsuccessful attempts, so successful authentication had to be identified by differences in the response content.

**Severity:** Critical

---

## FIND-B-002 — SQL Injection

The DVWA SQL Injection module remained exploitable at Medium security.

The vulnerable parameter was tested with **sqlmap**, which identified:

- Boolean-based blind SQL Injection
- Time-based blind SQL Injection

Database records and password hashes were successfully extracted.

**Severity:** Critical

---

## FIND-B-003 — Command Injection

The Medium security filter blocked some command separators but did not correctly handle all shell operators.

A bypass using the pipe operator allowed arbitrary operating-system command execution.

**commix** was then used to confirm the vulnerability and obtain a remote pseudo-terminal shell.

The assessment demonstrated execution under the web-server account.

**Impact:**

- Remote command execution
- Server-side shell access
- Sensitive file access

**Severity:** High

---

## FIND-B-004 — Unrestricted File Upload

The file-upload control relied on client-controlled filename validation.

By intercepting the upload request with **Burp Suite**, the filename could be modified in transit and a PHP webshell uploaded.

The uploaded webshell allowed server-side command execution.

**Impact:**

- Webshell deployment
- Remote command execution
- Sensitive server access

**Severity:** High

---

## FIND-B-005 — Reflected Cross-Site Scripting Filter Bypass

DVWA Medium attempted to block the `<script>` tag using a case-sensitive blacklist.

Changing tag capitalization bypassed the filter and allowed JavaScript execution.

**Impact:**

- Arbitrary JavaScript execution
- Session-cookie exposure
- Client-side compromise

**Severity:** Medium

---

## FIND-B-006 — Local File Inclusion

The Medium security control blocked relative path traversal sequences such as `../`, but did not prevent absolute file paths.

This allowed sensitive local files to be read.

Examples included operating-system and database configuration files.

**Impact:**

- Sensitive file disclosure
- Operating-system information exposure
- Database configuration disclosure

**Severity:** High

---

## FIND-B-007 — Cross-Site Request Forgery

The password-change functionality lacked effective CSRF protection.

The application did not implement:

- Anti-CSRF tokens
- Origin validation
- Referer validation

Sensitive operations were also performed through GET requests.

**Impact:**

- Unauthorized password changes
- Account compromise through victim interaction

**Severity:** High

---

## FIND-B-008 — Predictable Session Identifiers

The Weak Session IDs module generated session identifiers using predictable timestamp-based values.

The resulting entropy was insufficient for secure session management.

**Impact:**

- Session prediction
- Session hijacking risk
- Authentication compromise

**Severity:** High

---

# 7. Vulnerability Coverage

The penetration test covered a broad set of web-security weaknesses.

```text
Web Application Security
│
├── SQL Injection
├── Authentication Bypass
├── Brute Force
├── Broken Access Control / IDOR
├── Parameter Pollution
├── Cryptographic Failures
├── JWT Security
├── Security Misconfiguration
├── Cross-Site Scripting
├── Command Injection
├── Unrestricted File Upload
├── Local File Inclusion
├── CSRF
└── Predictable Session IDs
```

---

# 8. Exploitation Highlights

Several findings demonstrated significant real-world impact.

## Administrative Access

SQL Injection and authentication weaknesses enabled access to privileged accounts.

## Database Exfiltration

sqlmap was used to validate injection vulnerabilities and extract database records.

## Remote Command Execution

Command Injection and unrestricted file upload led to operating-system command execution.

```text
HTTP Request
     │
     ▼
Vulnerable Parameter
     │
     ▼
Filter Bypass
     │
     ▼
Command Injection
     │
     ▼
Remote Shell
```

## Sensitive File Disclosure

Local File Inclusion and security misconfiguration exposed files that should not have been accessible through the web application.

## Session Security

XSS, CSRF and predictable session identifiers demonstrated weaknesses in client-side and session-management controls.

---

# 9. OWASP, WSTG and MITRE ATT&CK

Each finding was documented using a structured format that included:

- Finding ID
- Vulnerability title
- OWASP category
- OWASP WSTG reference
- Technical description
- Root cause
- Vulnerable endpoint
- Proof of Concept
- CVSS v4 score
- MITRE ATT&CK mapping
- Mitigation recommendations
- Technical evidence

This structure was used to produce a penetration-test report closer to a professional security-assessment format rather than simply documenting challenge completion.

---

# 10. CVSS v4 Risk Assessment

Findings were assigned **CVSS v4** severity scores based on their technical impact and exploitation conditions.

The report includes vulnerabilities rated:

- **Critical**
- **High**
- **Medium**

Some of the highest-impact findings included:

- SQL Injection authentication bypass
- SQL Injection database extraction
- Missing brute-force protections
- Command Injection
- Unrestricted file upload
- Local File Inclusion
- Broken Access Control

---

# 11. Comparison Between Juice Shop and DVWA

A major part of the project was comparing how penetration-testing techniques transferred between the two applications.

## Directly Transferable Techniques

Several techniques remained effective with only minor changes.

### SQL Injection

SQL Injection was exploitable in both targets.

sqlmap was successfully used in both environments, with adjustments for:

- Database technology
- Request structure
- Authentication cookies

### Credential Attacks

Burp Suite Intruder was effective against authentication mechanisms in both applications.

However, successful authentication had to be detected differently depending on the target.

### Cross-Site Scripting

Reflected XSS was identified in both environments.

The core weakness remained insufficient handling of user-controlled output.

---

# 12. Techniques That Required Adaptation

DVWA Medium implemented additional controls, but several were incomplete and could be bypassed.

## Command Injection

Some shell separators were filtered, but alternative operators remained usable.

## File Upload

The application checked the filename submitted by the client but trusted client-controlled data.

Intercepting the request allowed the validation to be bypassed.

## Local File Inclusion

Relative traversal patterns were blocked, but absolute paths were still accepted.

## Cross-Site Scripting

A blacklist blocked one specific capitalization of the `<script>` tag but could be bypassed through variations.

## CSRF

No effective origin-validation mechanism or anti-CSRF token was present.

## Session IDs

Timestamp-derived session identifiers remained predictable.

---

# 13. Main Security Lesson

The DVWA Medium controls demonstrated a recurring defensive weakness:

```text
Client-Side Validation
        +
      Blacklists
        +
Partial Input Filtering
        │
        ▼
   Bypass Possible
```

Effective security requires:

```text
Server-Side Validation
        +
Positive Validation
        +
Secure-by-Design Controls
        │
        ▼
Stronger Application Security
```

Security decisions should not rely on data that can be modified by the client.

---

# 14. Key Recommendations

## SQL Injection

- Use prepared statements
- Avoid string concatenation in database queries
- Apply least privilege to database accounts
- Consider WAF protections as an additional defensive layer

## Authentication

- Implement rate limiting
- Implement temporary account lockout
- Add MFA
- Avoid deterministic or client-generated passwords
- Avoid exposing credentials in URLs

## Access Control

- Validate authorization for every resource
- Reject ambiguous or duplicated parameters
- Enforce authorization server-side

## Password Security

- Do not expose password hashes inside JWT payloads
- Replace weak hashing algorithms such as MD5
- Use modern password hashing such as bcrypt or Argon2

## Cross-Site Scripting

- Encode output correctly
- Sanitize untrusted input
- Use a restrictive Content Security Policy
- Avoid blacklist-based filtering

## Command Injection

- Avoid passing user input to shell commands
- Use strict positive input validation
- Accept only expected values and formats

## File Upload

- Validate file content server-side
- Verify MIME type and magic bytes
- Store uploads outside the webroot
- Disable execution permissions on uploaded content

## Local File Inclusion

- Use server-side allowlists
- Never directly concatenate user-controlled paths
- Reject absolute and unexpected file paths

## CSRF

- Use per-session anti-CSRF tokens
- Validate `Origin` and `Referer`
- Avoid GET requests for sensitive state-changing operations
- Use secure `SameSite` cookie policies

## Session Management

- Generate identifiers using a cryptographically secure random number generator
- Rotate session identifiers after authentication
- Configure cookies with:
  - `HttpOnly`
  - `Secure`
  - `SameSite`

---

# 15. Environment Limitations

The entire project was performed locally inside an isolated virtual machine.

This meant the environment did not reproduce the complete external attack surface of a real production application.

Some OWASP Juice Shop challenges were unavailable because of technical incompatibilities in the local environment.

Hydra and Medusa were also tested for authentication attacks, but the Juice Shop JSON authentication API was not compatible with their expected request format.

Burp Suite Intruder was therefore used successfully for the authentication tests.

---

# 16. Skills Demonstrated

This project demonstrates practical experience in:

- Web Application Penetration Testing
- PTES
- OWASP WSTG
- OWASP vulnerability classification
- CVSS v4 scoring
- MITRE ATT&CK mapping
- HTTP request analysis
- Proxy-based testing
- SQL Injection
- Broken Access Control
- IDOR
- Authentication testing
- Brute-force testing
- JWT analysis
- Cross-Site Scripting
- Command Injection
- File Upload security
- Local File Inclusion
- CSRF
- Session security
- Database exfiltration
- Remote command execution
- Proof-of-Concept development
- Vulnerability reporting
- Security mitigation design
- Burp Suite
- sqlmap
- gobuster
- ffuf
- commix
- Docker
- Kali Linux

---

# 17. Project Files

```text
module-3-web-application-penetration-testing/
├── README.md
├── report.pdf
├── presentation.pdf
└── video / demo
```

The repository contains the complete penetration-testing report and presentation.

## Report

[View the penetration-testing report](./report.pdf)

## Presentation

[View the project presentation](./presentation.pdf)

---

# 18. Academic Context

**Course:** Cybersecurity Laboratories  
**Module:** Module 3 — Web Application Penetration Testing  
**Institution:** University of Minho — School of Engineering  
**Academic Year:** 2025/2026

---

# 19. Ethical Use

This repository documents penetration testing performed exclusively against **intentionally vulnerable applications in an isolated and controlled laboratory environment**.

The techniques described here are presented for:

- Cybersecurity education
- Defensive security research
- Vulnerability assessment
- Ethical penetration testing

No production or third-party systems were targeted during this project.
