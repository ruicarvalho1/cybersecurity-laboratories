# Wazuh Lab

A self-contained SIEM lab built on [Wazuh](https://wazuh.com) 4.14.
A monitored victim host runs a realistic-looking corporate web portal.
Over three labs you set up the environment, analyse vulnerabilities,
and investigate a simulated multi-stage attack.

---

## Prerequisites

- **Docker Desktop** ≥ 4.x (or Docker Engine + Compose v2), running
  with at least **6 GB RAM** allocated to Docker
- A terminal and a modern browser
- Git (to fork and submit work)

---

## Quick start

```bash
git clone https://github.com/<your-username>/wazuh-lab
cd wazuh-lab
docker compose pull
docker compose up -d
```

Open **https://localhost** in your browser, accept the self-signed
certificate, and log in with **admin / SecretPassword**.
The dashboard takes 1–3 minutes to become ready after `up`.

The victim portal is at **http://localhost:8080**.

---

## Lab structure

| File | Description |
|---|---|
| `docker-compose.yml` | Brings up the full stack |
| `config/custom-rules/local_rules.xml` | **Your working file** — edit rules here |
| `config/custom-rules/local_decoder.xml` | Custom log decoder |
| `config/wazuh_agent/ossec.conf` | Wazuh agent config (FIM paths, log sources) |
| `labs/lab1-setup-and-tour.md` | Lab 1 — setup and dashboard tour |
| `labs/lab2-vulnerability-detection.md` | Lab 2 — passive CVE detection and attack simulation |
| `labs/lab3-investigation.md` | Lab 3 — live attack, rule tuning, kill-chain reconstruction |

---

## Labs

### Lab 1 — Setup and dashboard tour
Bring the stack up, explore the Wazuh dashboard, trigger FIM events,
and write your first custom detection rules.

### Lab 2 — Vulnerability detection
Explore passive CVE findings on the victim, then run a series of
attack probes (Shellshock, XSS, SQLi, reconnaissance) and observe
how Wazuh classifies them with MITRE ATT&CK techniques.

### Lab 3 — Investigation
Enable the hidden attacker (`--profile attack`), watch a multi-stage
attack unfold in real time, and reconstruct the kill chain from the
alerts. You will tune rule levels, add MITRE tags, and write
correlation rules.

---

## Useful commands

```bash
# Reload rules after editing local_rules.xml
docker compose restart wazuh.manager

# Open a shell on the victim
docker compose exec victim bash

# Enable the attacker (Lab 3)
docker compose --profile attack up -d

# Reset everything and start fresh
docker compose down -v && docker compose up -d
```

---

## Submitting your work

This repo is designed to be forked. Your deliverable lives entirely
in two files that are bind-mounted into the running stack:

- `config/custom-rules/local_rules.xml` — your tuned detection rules
- `config/wazuh_agent/ossec.conf` — any agent config changes

Commit your changes and push to your fork. Share the fork URL with
your instructor.

```bash
git add config/custom-rules/local_rules.xml config/wazuh_agent/ossec.conf
git commit -m "Lab 3 — tuned rules and MITRE annotations"
git push
```

> Nothing else needs to be committed — certificates, image files, and
> generated data are either auto-created or too large for Git.
> A `.gitignore` is included to keep the repo clean.

---

## Wazuh dashboard credentials

| Component | URL | Username | Password |
|---|---|---|---|
| Dashboard | https://localhost | admin | SecretPassword |
| Victim portal | http://localhost:8080 | — | — |
