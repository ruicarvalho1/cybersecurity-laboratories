import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("../logs/ca_server/events.jsonl")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def log_event(event_type: str, severity: str, details: dict):
    """Base function — writes any event to the log file."""
    record = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "severity": severity,
        "log_source": "ca_server",
        **details
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")

    print(f"[{severity}] {event_type}: {details}")


# ─────────────────────────────────────────
# Normal operational events
# ─────────────────────────────────────────

def log_cert_issued(username: str, cert_serial: str):
    """Log certificate issuance."""
    log_event("cert_issued", "INFO", {
        "username": username,
        "cert_serial": cert_serial
    })


def log_cert_validated(username: str, result: bool):
    """Log certificate validation result."""
    log_event("cert_validated", "INFO", {
        "username": username,
        "validation_result": "ok" if result else "failed"
    })


def log_integrity_check_passed(cert_count: int):
    """Log successful integrity verification."""
    log_event("integrity_check_passed", "INFO", {
        "certs_checked": cert_count,
        "violations_found": 0
    })


# ─────────────────────────────────────────
# Security violation events
# ─────────────────────────────────────────

def log_ca_cert_tampered(cert_id: str, expected_hash: str,
                         actual_hash: str, cert_type: str = "ca"):
    """Log CA certificate tampering."""
    severity = "CRITICAL" if cert_type == "ca" else "WARNING"

    log_event("ca_cert_tampered", severity, {
        "cert_id": cert_id,
        "cert_type": cert_type,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "triggered_rule": "RULE-001: CERT_HASH_MISMATCH",
        "mitre_technique": "T1565.001 - Stored Data Manipulation",
        "mitre_tactic": "Tampering",
        "recommended_action": "Isolate CA Server and revoke affected certificates"
    })


def log_user_cert_tampered(cert_id: str, username: str,
                           expected_hash: str, actual_hash: str):
    """Log user certificate modification."""
    log_event("user_cert_tampered", "WARNING", {
        "cert_id": cert_id,
        "username": username,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "triggered_rule": "RULE-001: CERT_HASH_MISMATCH",
        "mitre_technique": "T1565.001 - Stored Data Manipulation",
        "mitre_tactic": "Tampering",
        "recommended_action": "Revoke the user's certificate and reissue a new one"
    })


def log_external_connection(client_ip: str, db_user: str):
    """Log external connection attempts to the database."""
    log_event("external_db_connection", "WARNING", {
        "client_ip": client_ip,
        "db_user": db_user,
        "triggered_rule": "RULE-003: EXTERNAL_DB_CONNECTION",
        "mitre_technique": "T1190 - Exploit Public-Facing Application",
        "mitre_tactic": "Initial Access"
    })


def log_exfiltration_attempt(client_ip: str, query_rate: int):
    """Log suspected data exfiltration attempts."""
    log_event("exfiltration_suspected", "CRITICAL", {
        "client_ip": client_ip,
        "queries_per_30s": query_rate,
        "threshold": 20,
        "triggered_rule": "RULE-004: BULK_CERT_SELECT_EXTERNAL",
        "mitre_technique": "T1005 - Data from Local System",
        "mitre_tactic": "Collection"
    })