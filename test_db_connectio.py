import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env (if you're using one)
load_dotenv()

def test_postgres_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()

        print("✅ Connected to PostgreSQL")

        # Fetch some tool data
        cur.execute("""
            SELECT name, short_description, source, type
            FROM ai_tools
            WHERE type = 'new'
            LIMIT 10;
        """)
        results = cur.fetchall()

        if not results:
            print("⚠️ No 'new' tools found in the database.")
        else:
            print(f"✅ Retrieved {len(results)} tools:")
            for tool in results:
                print(f"🔹 {tool[0]} - {tool[1]} ({tool[2]}, {tool[3]})")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")

if __name__ == "__main__":
    test_postgres_connection()
