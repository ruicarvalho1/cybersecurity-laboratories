import os
import sys
import time
import psycopg2


DB_CONFIG = {
    "host": os.getenv("CA_DB_HOST", "localhost"),
    "port": int(os.getenv("CA_DB_PORT", "5432")),
    "dbname": os.getenv("CA_DB_NAME", "ca_server"),
    "user": os.getenv("CA_DB_USER", "caserver"),
    "password": os.getenv("CA_DB_PASSWORD", "caserver"),
}

DETECTION_WAIT_SECONDS = int(os.getenv("DETECTION_WAIT_SECONDS", "12"))


def connect():
    """Create a database connection."""
    return psycopg2.connect(**DB_CONFIG)


def scenario_1_ca_substitution():
    """Replace the CA certificate directly in the database."""
    print("\n" + "=" * 55)
    print("SCENARIO 1: CA Certificate Substitution")
    print("=" * 55)

    conn = connect()
    cur = conn.cursor()

    try:
        # Save original CA certificate
        cur.execute("SELECT ca_cert_id, ca_cert FROM certs_cacertificate LIMIT 1;")
        row = cur.fetchone()
        if not row:
            print("-> [ERROR] No CA certificate found in certs_cacertificate.")
            return

        cert_id, original = row
        print(f"-> Target CA certificate ID: {cert_id}")

        # Replace with fake certificate
        print("-> [ATTACK] Replacing CA certificate in database...")
        cur.execute(
            """
            UPDATE certs_cacertificate
            SET ca_cert = %s
            WHERE ca_cert_id = %s;
            """,
            (
                "-----BEGIN CERTIFICATE-----\n"
                "FAKE_CA_CERT_SUBSTITUTED_BY_ATTACKER\n"
                "-----END CERTIFICATE-----",
                cert_id,
            ),
        )
        conn.commit()
        print("-> [ATTACK] CA certificate replaced!")
        print(f"-> [MONITOR] Waiting for detection (<{DETECTION_WAIT_SECONDS}s)...")

        time.sleep(DETECTION_WAIT_SECONDS)

        # Restore original certificate
        print("-> [RESTORE] Restoring original CA certificate...")
        cur.execute(
            """
            UPDATE certs_cacertificate
            SET ca_cert = %s
            WHERE ca_cert_id = %s;
            """,
            (original, cert_id),
        )
        conn.commit()
        print("-> [RESTORE] CA certificate restored.")

    finally:
        cur.close()
        conn.close()


def scenario_2_user_cert_tampering():
    """Modify a user certificate directly in the database."""
    print("\n" + "=" * 55)
    print("SCENARIO 2: User Certificate Tampering")
    print("=" * 55)

    conn = connect()
    cur = conn.cursor()

    try:
        # Get one user certificate
        cur.execute(
            "SELECT user_id, username, certificate_pem FROM certs_usercertificate LIMIT 1;"
        )
        row = cur.fetchone()
        if not row:
            print("-> [ERROR] No user certificate found in certs_usercertificate.")
            return

        user_id, username, original_pem = row
        print(f"-> Target user: {username} (ID: {user_id})")

        # Modify certificate
        print(f"-> [ATTACK] Modifying certificate for user '{username}'...")
        cur.execute(
            """
            UPDATE certs_usercertificate
            SET certificate_pem = %s
            WHERE user_id = %s;
            """,
            (
                f"-----BEGIN CERTIFICATE-----\n"
                f"FAKE_CERT_FOR_{username.upper()}\n"
                f"-----END CERTIFICATE-----",
                user_id,
            ),
        )
        conn.commit()
        print("-> [ATTACK] User certificate modified!")
        print(f"-> [MONITOR] Waiting for detection (<{DETECTION_WAIT_SECONDS}s)...")

        time.sleep(DETECTION_WAIT_SECONDS)

        # Restore original certificate
        print("-> [RESTORE] Restoring original user certificate...")
        cur.execute(
            """
            UPDATE certs_usercertificate
            SET certificate_pem = %s
            WHERE user_id = %s;
            """,
            (original_pem, user_id),
        )
        conn.commit()
        print("-> [RESTORE] User certificate restored.")

    finally:
        cur.close()
        conn.close()


def scenario_3_external_connection():
    """Simulate external database access by writing events directly via ca_logger."""
    print("\n" + "=" * 55)
    print("SCENARIO 4: External Database Connection and Exfiltration")
    print("=" * 55)

    from ca_logger import log_external_connection, log_exfiltration_attempt

    attacker_ip = "198.51.100.17"

    print(f"-> [ATTACK] External connection from {attacker_ip}...")
    log_external_connection(client_ip=attacker_ip, db_user="caserver")
    time.sleep(1)

    print("-> [ATTACK] Query rate increasing...")
    for rate in [50, 65, 80, 100]:
        log_exfiltration_attempt(client_ip=attacker_ip, query_rate=rate)
        time.sleep(0.5)

    print(f"-> [MONITOR] CRITICAL: {attacker_ip} blocked!")


SCENARIOS = {
    "1": scenario_1_ca_substitution,
    "2": scenario_2_user_cert_tampering,
    "3": scenario_3_external_connection,
}


def main():
    print("CA SECURITY ATTACK SIMULATOR")
    print("Testing direct database tampering and simulated suspicious access scenarios")

    arg = sys.argv[1] if len(sys.argv) > 1 else "all"

    if arg == "all":
        for idx, fn in enumerate(SCENARIOS.values(), start=1):
            fn()
            if idx < len(SCENARIOS):
                print("-> Waiting 2 seconds before next scenario...")
                time.sleep(2)
    elif arg in SCENARIOS:
        SCENARIOS[arg]()
    else:
        print("Usage: python simulate_attacks_db.py [1|2|3|4|all]")
        sys.exit(1)

    print("\nSimulation complete.")
    print("   Check Grafana alerts, dashboard, and Elasticsearch logs.")


if __name__ == "__main__":
    main()