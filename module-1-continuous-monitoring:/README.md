# Module 1 — Continuous Security Monitoring & Threat Detection

## Overview

This project was developed as part of **Cybersecurity Laboratories — Module 1** at the University of Minho.

The objective of this module was to design and implement a **continuous security monitoring architecture** for a secure peer-to-peer auction platform.

The work combines:

- Threat modeling
- Continuous security monitoring
- Cyber Threat Intelligence (CTI)
- Open Source Intelligence (OSINT)
- Certificate integrity verification
- Security event collection and analysis
- Automated alerting
- Attack simulation

The main monitoring target is the system's **Certificate Authority (CA)**, as it represents a critical component of the platform's chain of trust.

---

## System Architecture

The monitored application is a secure peer-to-peer auction platform composed of several independent components.

### Main Components

- **Login Client** — Handles user authentication and local credentials.
- **Auction Client** — Coordinates user interaction with auctions and communicates with the remaining services.
- **CA Server** — Issues and manages X.509 certificates and authentication information.
- **TSA Server** — Provides trusted timestamps for transactions.
- **Peer Server** — Manages peer discovery and communication.
- **Blockchain / Smart Contracts** — Stores auction transactions and state in an immutable manner.
- **PostgreSQL Database** — Stores CA and user certificate information.

The separation of responsibilities between these components reduces the impact of a compromise and provides clear trust boundaries for security analysis.

---

## Security Requirements

The auction system was designed around several core security properties:

- **Authentication**
- **Integrity**
- **Non-repudiation**
- **Anonymity**
- **Verifiable timestamps**
- **Controlled identity disclosure**

X.509 certificates are used to authenticate entities, while digital signatures and blockchain records provide integrity and non-repudiation.

The Timestamp Authority provides signed timestamps for transactions.

---

## Threat Modeling

The system was analyzed using the **STRIDE threat-modeling methodology**.

The following threat categories were considered:

| STRIDE Category | Example Risk |
|---|---|
| Spoofing | Impersonation using compromised credentials |
| Tampering | Modification of certificates or stored information |
| Repudiation | Denying actions when reliable audit records are unavailable |
| Information Disclosure | Exposure of certificates, private information or auction data |
| Denial of Service | Making critical services unavailable |
| Elevation of Privilege | Obtaining unauthorized administrative privileges |

Threats were mapped across the major system components, including the CA Server, TSA Server, Peer Server, blockchain, auction clients, local files and the CA database.

---

## Security Framework Mapping

The STRIDE analysis was complemented with established cybersecurity frameworks.

### MITRE ATT&CK

MITRE ATT&CK techniques were used to associate identified threats with realistic attacker behaviors and Tactics, Techniques and Procedures (TTPs).

Examples include:

- `T1565.001` — Stored Data Manipulation
- `T1553.004` — Install Root Certificate
- `T1078` — Valid Accounts
- `T1498` — Network Denial of Service
- `T1068` — Exploitation for Privilege Escalation

### NIST SP 800-137

NIST SP 800-137 was used as the basis for the continuous monitoring strategy.

The objective was to translate high-level threats into:

- Observable events
- Security metrics
- Detection thresholds
- Alerting rules
- Automated response actions

---

## Continuous Monitoring Architecture

The monitoring architecture follows a layered model.

```text
Application / Database
        │
        ▼
Security Events & Integrity Checks
        │
        ▼
      Filebeat
        │
        ▼
   Elasticsearch
        │
        ▼
      Grafana
        │
        ▼
Dashboards + Alerts + Email Notifications
