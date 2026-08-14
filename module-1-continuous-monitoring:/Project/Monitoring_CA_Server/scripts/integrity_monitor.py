import os
import time
import hashlib
import psycopg2
from ca_logger import (
    log_integrity_check_passed,
    log_ca_cert_tampered,
    log_user_cert_tampered,
    log_external_connection,
    log_event
)

DB_CONFIG = {
    "host":     os.getenv("CA_DB_HOST",     "localhost"),
    "port":     int(os.getenv("CA_DB_PORT", "5432")),
    "dbname":   os.getenv("CA_DB_NAME",     "ca_server"),
    "user":     os.getenv("CA_DB_USER",     "caserver"),
    "password": os.getenv("CA_DB_PASSWORD", "caserver"),
}

INTERVAL = int(os.getenv("MONITOR_INTERVAL", "10"))


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def connect_db():
    """Establish connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("[MONITOR] Connected to database")
        return conn
    except Exception as e:
        print(f"[MONITOR] Connection error: {e}")
        return None


def build_baseline(conn):
    """Compute initial hashes and store them in the database as the integrity baseline."""
    with conn.cursor() as cur:
        # CA certificate baseline
        cur.execute("SELECT ca_cert_id, ca_cert FROM certs_cacertificate;")
        for cert_id, ca_cert in cur.fetchall():
            h = sha256(ca_cert)
            cur.execute("""
                UPDATE certs_cacertificate
                SET hash_sha256 = %s
                WHERE ca_cert_id = %s AND (hash_sha256 = '' OR hash_sha256 IS NULL);
            """, (h, cert_id))

        # User certificate baseline
        cur.execute("SELECT user_id, certificate_pem FROM certs_usercertificate;")
        for user_id, cert_pem in cur.fetchall():
            h = sha256(cert_pem)
            cur.execute("""
                UPDATE certs_usercertificate
                SET hash_sha256 = %s
                WHERE user_id = %s AND (hash_sha256 = '' OR hash_sha256 IS NULL);
            """, (h, user_id))

    conn.commit()
    print("[MONITOR] Baseline hashes stored in database.")
    log_event("baseline_established", "INFO", {"message": "Initial certificate hashes stored in database"})


def check_integrity(conn):
    """Verify integrity of CA and user certificates by comparing stored hashes."""
    violations = 0

    with conn.cursor() as cur:
        # Check CA certificates
        cur.execute("SELECT ca_cert_id, ca_cert, hash_sha256 FROM certs_cacertificate;")
        for cert_id, ca_cert, stored_hash in cur.fetchall():
            current_hash = sha256(ca_cert)
            if current_hash != stored_hash:
                print(f"[MONITOR] CRITICAL: CA certificate hash mismatch! ID {cert_id}")
                log_ca_cert_tampered(str(cert_id), stored_hash, current_hash, cert_type="ca")
                cur.execute("""
                    UPDATE certs_cacertificate
                    SET hash_sha256 = %s WHERE ca_cert_id = %s;
                """, (current_hash, cert_id))
                violations += 1

        # Check user certificates
        cur.execute("SELECT user_id, username, certificate_pem, hash_sha256 FROM certs_usercertificate;")
        for user_id, username, cert_pem, stored_hash in cur.fetchall():
            current_hash = sha256(cert_pem)
            if current_hash != stored_hash:
                print(f"[MONITOR] WARNING: Certificate hash mismatch for user {username}")
                log_user_cert_tampered(str(user_id), username, stored_hash, current_hash)
                cur.execute("""
                    UPDATE certs_usercertificate
                    SET hash_sha256 = %s WHERE user_id = %s;
                """, (current_hash, user_id))
                violations += 1

    conn.commit()

    if violations == 0:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM certs_cacertificate;")
        ca_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM certs_usercertificate;")
        user_count = cur.fetchone()[0]
        log_integrity_check_passed(cert_count=ca_count + user_count)

    return violations


def check_external_connections(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT pid, usename, client_addr
            FROM pg_stat_activity
            WHERE datname = %s
              AND client_addr IS NOT NULL
              AND family(client_addr) = 4
              AND NOT (client_addr << inet '127.0.0.0/8')
              AND NOT (client_addr << inet '::1/128');
        """, (DB_CONFIG["dbname"],))
        rows = cur.fetchall()
    for pid, user, addr in rows:
        print(f"[MONITOR] Ligação externa: {addr}")
        log_external_connection(client_ip=str(addr), db_user=user)

def run():
    """Main monitoring loop."""
    print("[MONITOR] Starting certificate integrity monitor")
    print(f"[MONITOR] Interval: {INTERVAL}s | Database: {DB_CONFIG['host']}/{DB_CONFIG['dbname']}")

    conn = None
    baseline_built = False

    while True:
        try:
            if conn is None:
                conn = connect_db()
                if conn is None:
                    time.sleep(INTERVAL)
                    continue

            if not baseline_built:
                build_baseline(conn)
                baseline_built = True

            violations = check_integrity(conn)
            if violations > 0:
                print(f"[MONITOR] {violations} integrity violation(s) detected!")
            else:
                print(f"[MONITOR] OK — system integrity verified.")

            check_external_connections(conn)

        except Exception as e:
            print(f"[MONITOR] Error during monitoring: {e}")
            try:
                if conn:
                    conn.close()
            except Exception:
                pass
            conn = None

        time.sleep(INTERVAL)


if __name__ == "__main__":
    run()