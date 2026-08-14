# Lab 1 — Setup and dashboard tour

> Prerequisites: Docker Desktop running (≥ 16 GB RAM recommended), a
> terminal, a modern browser.

**Wazuh** is an open-source SIEM (Security Information and Event Management) and XDR
(Extended Detection and Response) platform. It collects logs and telemetry from monitored
hosts via lightweight agents, parses and correlates that data against a rule set on a
central manager, and indexes the resulting alerts in OpenSearch so analysts can search,
filter, and visualise them. Beyond log analysis, the same agent drives file integrity
monitoring, vulnerability detection, configuration assessment, and active response.

The goal of this lab is to bring up the SIEM environment and learn
your way around the Wazuh dashboard. There will be no critical events yet.
The events you will see are baseline activity.

---

## Bring the lab up

From inside the `wazuh-lab` folder:

```bash
docker compose pull
docker compose up -d
```

Wait 2–3 minutes, then open `https://localhost`, accept the
self-signed certificate, and log in as `admin` / `SecretPassword`.

`docker compose ps` should show four relevant services running: `wazuh.manager`,
`wazuh.indexer`, `wazuh.dashboard`, `victim`.

The `victim` is a Linux container that simulates a production host: it runs Apache and a few other services, all with a Wazuh agent installed and reporting
to the manager. Everything you observe in the dashboard originates from this host.

To start over: `docker compose down -v && docker compose up -d`.

---

## Tour the dashboard

Click through the sections below.

* **Wazuh home** — agent overview. Find the `victim` agent and confirm
  it is **Active**.
* **Threat Hunting → Events** — the unified event stream. Every parsed
  log line, FIM event, syscollector record, etc. lands here.
* **Vulnerability Detection** — the vulnerability detector's CVE list for the
  victim. We will look at it in Lab 2.
* **File Integrity Monitoring** — FIM events. Mostly quite right now.
* **Inventory data** — packages, ports, processes, hardware, all
  collected by the agent's `syscollector` module.

### Reading an event

Expand any event in **Threat Hunting → Events**. The most useful fields are:

| Field | Meaning |
|---|---|
| `agent.name` | Which host generated the event |
| `rule.id` | Numeric ID of the rule that matched |
| `rule.description` | Human-readable description of the rule |
| `rule.level` | Severity on a 0–15 scale (≥ 7 is medium, ≥ 12 is high) |
| `rule.groups` | Category tags, e.g. `syscheck` |
| `full_log` | The original raw log line before parsing |

Add as a note: Rule IDs are not random — they encode the log source.
If you click on each, if will show more details on the ID and ID categories.

### Filtering events

You can filter in the search bar using KQL syntax, or click any field
value in an expanded event to pin it as a filter.

Useful starting points:

```
rule.groups: syscheck              # only FIM events
rule.groups: authentication        # only login/auth events
rule.level >= 7                    # skip noisy low-level events
agent.name: victim                 # narrow to one host
rule.id: 554                       # specific rule — file added
```

Combine filters with `AND`, e.g. `agent.name: victim AND rule.level >= 7`.
To remove a filter, click the × next to it in the filter bar above the table.

---

## Trigger FIM

Open a shell inside the victim container:

```bash
docker compose exec victim bash
```

Then create a dummy file in a monitored directory:

```bash
touch /etc/test_wazuh
```

Within minutes, the manager should report a new file creation.
You can try modifying the file, changing permissions, deleting, etc.

This worked because `/etc` is one of the default monitored directories.
The victim's Wazuh agent configuration is mounted from `config/wazuh_agent/ossec.conf`
in your working directory. Open it and add a new entry inside the `<syscheck>` block, e.g.:

```xml
<directories report_changes="yes" realtime="yes">/var/www/html</directories>
```

Restart the victim to apply the change:
```bash
docker compose restart victim
```

This time, all changes that Apache makes to HTML pages will be logged.
To trigger a FIM event, edit the portal's main page from your host:

```bash
echo "<\!-- updated -->" >> images/victim/html/index.html
```

Wazuh should report a modification to `/var/www/html/index.html` within seconds.

---

## Browse the victim portal

The victim's Apache server is exposed at `http://localhost:8080`. Open it in your browser.
You should see a mock corporate intranet page.

Make a request to it — the access log is forwarded to Wazuh in real time. In
**Threat Hunting → Events**, filter `rule.groups: web` and watch the Apache access log
events appear as you navigate.

---

## Write a custom rule

Custom rules live in `config/custom-rules/local_rules.xml`, mounted into
the manager. The lab ships one already; you'll work with it later.
For now, add a tiny rule of your own and watch it fire.

Open `config/custom-rules/local_rules.xml` in an editor and add a new
rule inside the existing `<group>` block:

```xml
<rule id="100199" level="7">
  <if_sid>31101</if_sid>
  <url>/lab1-demo</url>
  <description>lab1 demo: someone hit /lab1-demo</description>
</rule>
```

`/lab1-demo` doesn't exist on the victim, so Apache returns 404, which fires built-in rule **31101** (any 4xx response). By writing `<if_sid>31101</if_sid>` our rule sits one level deeper in the chain and wins when the URL also matches.

Reload the manager so it picks up the change:

```bash
docker compose restart wazuh.manager
```

Generate a hit directly from your terminal — the victim's Apache is now on port 8080:

```bash
curl http://localhost:8080/lab1-demo
```

Back in **Threat Hunting → Events**, filter `rule.id: 100199`. Your
rule should fire within a few seconds.

---

## Rule syntax deep dive

The rule you just wrote matches on a single field. Wazuh's rule language has three more constructs worth knowing.

> After any edit to `local_rules.xml`, run `docker compose restart wazuh.manager` before testing.

### Inheritance with `if_sid`

A child rule only fires when a parent has already fired for the same event.
This lets you narrow down a broad built-in rule without touching the built-in rule set.
The child inherits the parent's decoded fields, so you can match on sub-patterns that only make sense in context.

Add this rule:

```xml
<rule id="100200" level="10">
  <if_sid>31100</if_sid>
  <url>etc/passwd|etc/shadow</url>
  <description>Possible Local File Inclusion attempt</description>
</rule>
```

Trigger it:

```bash
curl "http://localhost:8080/index.php?file=../../../../etc/passwd"
```

Find the alert in **Threat Hunting → Events** and confirm rule 100200 fired alongside its parent.

> What is rule 31100? Find its description in the dashboard
> (click the rule ID in an event, or look under **Rules** in the management menu).

### Frequency-based rules

Wazuh can count how many times a parent rule fires within a sliding time window and raise a new alert only when a threshold is crossed.
This is useful for catching brute-force and reconnaissance patterns that look innocent one request at a time.

Add this rule:

```xml
<rule id="100201" level="10" frequency="8" timeframe="30">
  <if_matched_sid>31101</if_matched_sid>
  <description>Web Reconnaissance: Multiple 404 errors from same IP</description>
</rule>
```

Trigger it by generating a burst of 404 responses:

```bash
for i in {1..10}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/probe-$i; done
```

Watch for rule 100201 to fire after the eighth hit within the 30-second window.

> What is rule 31101? Find its description in the dashboard — it is the parent this frequency rule counts.

### Negative matching — suppressing noise

A child rule with `level="0"` silences its parent for a specific sub-case.
The event is still parsed but generates no alert.
This is the standard way to suppress recurring low-value events without disabling the parent rule entirely.

For example, suppose you want to silence 404s for a known-safe path like `/status` that your monitoring stack pings constantly.
Rule 31101 fires for every 4xx response; a level-0 child suppresses only the specific URL:

```xml
<rule id="100202" level="0">
  <if_sid>31101</if_sid>
  <url>^/status$</url>
  <description>Suppress 404 for /status health-check path</description>
</rule>
```

After reloading the manager, `curl http://localhost:8080/status` will no longer appear as an alert.

> **Note:** Wazuh's built-in rule 31102 already suppresses 404s for common static-asset extensions (`.ico`, `.jpg`, `.css`, `.js`, …).
> If you try to suppress `favicon.ico` yourself you will find that 31102 handles it first.
> Always check the existing rule set before writing a suppression — you may already have coverage.

