import os, sys, psycopg2
from getpass import getpass
from dotenv import set_key

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
SCHEMA_SQL = os.path.join(BASE_DIR, "db", "schema.sql")
SEED_SQL   = os.path.join(BASE_DIR, "db", "seed.sql")
ENV_PATH   = os.path.join(BASE_DIR, ".env")

def run_file(conn, path):
    with open(path, "r", encoding="utf-8") as f:
        conn.cursor().execute(f.read())
    conn.commit()
    print(f"  OK  {os.path.basename(path)}")

def main():
    print("\nLoanIQ — Interactive Database Setup\n")
    print("Please provide your PostgreSQL credentials (they will be saved to .env).")
    
    host     = input("Host [localhost]: ").strip() or "localhost"
    port     = input("Port [5432]: ").strip() or "5432"
    dbname   = input("Database Name [loandb]: ").strip() or "loandb"
    user     = input("User [postgres]: ").strip() or "postgres"
    password = getpass("Password: ").strip()

    print(f"\nConnecting to {host}:{port}/{dbname} as {user}...")

    try:
        conn = psycopg2.connect(
            host=host, port=int(port), dbname=dbname, user=user, password=password
        )
    except psycopg2.OperationalError as e:
        print(f"\n[ERROR] Connection failed: {e}")
        sys.exit(1)

    print("Success! Connection established.")
    
    # Save to .env
    set_key(ENV_PATH, "DB_HOST", host)
    set_key(ENV_PATH, "DB_PORT", port)
    set_key(ENV_PATH, "DB_NAME", dbname)
    set_key(ENV_PATH, "DB_USER", user)
    set_key(ENV_PATH, "DB_PASSWORD", password)
    print("Credentials saved to .env file.")

    print("\nRunning SQL scripts...")
    run_file(conn, SCHEMA_SQL)
    run_file(conn, SEED_SQL)

    print("\nRow counts:")
    tables = ["customer","income_details","address_details","credit_history","risk_category",
              "credit_score","loan_type","loan","loan_status_history","guarantor",
              "emi_schedule","repayment","default_record","penalty"]
    with conn.cursor() as cur:
        for t in tables:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            print(f"  {t:<25} {cur.fetchone()[0]:>5}")
    conn.close()
    print("\nDone. Run:  streamlit run app/main.py\n")

if __name__ == "__main__":
    main()
