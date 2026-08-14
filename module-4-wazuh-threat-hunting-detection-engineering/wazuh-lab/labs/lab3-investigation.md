# Lab 3 — Investigation

> Prerequisites: Labs 1 and 2 complete. You are comfortable navigating
> the dashboard and you've seen the vulnerability list.

In this lab a hidden attacker runs against the victim and you observe
what Wazuh sees. Custom rules are already in place to surface relevant
events. Your job is to interpret them, improve them, and reconstruct
what happened.

---

## Bring the attacker up

If the lab is already running, restart with the attacker enabled:

```bash
docker compose down -v
docker compose --profile attack up -d
```

The attacker will idle for ~60 seconds and then execute a sequence of
steps over the next several minutes. Open **Threat Hunting → Events**
with auto-refresh on, and watch.

The full chain takes up to 10 minutes to complete. Exactly 5 CVEs from
the vulnerability list you saw in Lab 2 are exercised.

---

## Watch the attack unfold

Go to **Threat Hunting → Events** and let events accumulate.
Pivot freely: click rule IDs to scope, expand
events to inspect `full_log`, visit **File Integrity Monitoring** to
see diffs on sensitive files.

Cross-reference the **Vulnerabilities** view from Lab 2. Of the
roughly 70 CVEs flagged, only 5 are actually exercised by the attacker.
Can you find which ones?

---

## Tune the rules

Before you can read the attack story from the dashboard, you need to separate signal from noise. Work through these three steps in order.

### Step 1 — Identify and suppress noise

Open **Threat Hunting → Events** with the attacker running and scan the stream. Not every alert is meaningful: background traffic, health-check pings, and expected errors all fire rules. Before tuning the attack rules, it helps to silence the clutter.

For each recurring event that represents known-benign activity:

* Is there already a built-in suppression rule for it (level 0)? Check whether a child of the firing rule already exists.
* If not, write a level-0 rule that chains from the noisy rule and matches the specific sub-pattern you want to silence.

After reloading the manager, the dashboard should be noticeably quieter. The remaining events are more likely to carry real signal.

### Step 2 — Identify the attack events

Open `config/custom-rules/local_rules.xml` and read through all active rules. For each rule that has fired:

* What event does the pattern actually catch? How specific is it?
* Which attack class (CVE, MITRE technique) does it correspond to?
* Is the severity level appropriate — would an analyst act on this immediately, or treat it as low-priority?
* Are MITRE ATT&CK IDs or group tags missing that would help categorise the alert?

Cross-reference the **Vulnerabilities** view from Lab 2. Which of the roughly 70 CVEs you saw there map to the rules that fired?

### Step 3 — Improve the attack rules

With a clear view of which rules are carrying signal, make targeted improvements:

**Severity.** Raise the level of rules whose threat warrants it. Levels ≥ 12 send email in a default Wazuh deployment; level 15 is the maximum. A rule that fires on a real attack should not sit at level 3.

**MITRE and groups.** Add `<mitre><id>T…</id></mitre>` and `<group>` tags to rules that lack them. This populates the MITRE ATT&CK view and makes the alerts searchable by technique.

**Correlation.** Some individual events are ambiguous; pairs are not. Express that using `<if_matched_sid>` and `<timeframe>`. For example, a JNDI lookup (100130) followed by a `/etc/passwd` modification (100150) within a short window is a much stronger signal than either alone.

### Applying changes

To test a rule change without clearing the event history, you can restart only the manager:

```bash
docker compose restart wazuh.manager
```

This reloads the rule set and lets you re-examine existing events with updated logic.
The attack events already in the index are re-evaluated as new events arrive.

To re-run the full attack chain from scratch (clearing all history):

```bash
docker compose down -v && docker compose --profile attack up -d
```

If a rule fails to load, check the manager log:

```bash
docker compose logs wazuh.manager | grep -i 'rules\|error\|xml'
```

---

## Reflection

Your goal is to present findings as if reporting to a security team:

1. **Reconstruct the attack.** Using only the alerts and FIM events
   visible in the dashboard, tell the story of what the attacker did,
   in order. Which CVEs were exploited? What did the attacker achieve
   at each step? What evidence supports each claim?

2. **Assess the rule set.** Which rules gave the strongest signal?
   Which were too noisy or too quiet? What would you add if you were
   hardening this SIEM for production?

3. **Compare with your Lab 2 prediction.** Did the attacker exploit the
   CVEs you expected? Were there surprises?
