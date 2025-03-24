import csv
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# CSV file path - update this to your file's location
csv_file_path = '/Users/travisfleisher/Desktop/ToolCurator.AI - Sheet1.csv'


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


def import_csv_to_postgres():
    # Read CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Connect to PostgreSQL
    conn = get_db_connection()
    cur = conn.cursor()

    # Track successful imports
    processed_count = 0
    skipped_count = 0
    duplicate_url_count = 0

    # Process each row
    for row in rows:
        # Prepare values
        name = row.get('name', '').strip()
        category = row.get('category', '').strip()
        source = row.get('source', '').strip()
        source_url = row.get('source_url', '').strip()
        short_description = row.get('short_description', '').strip()
        full_description = row.get('full_description', '').strip() or None
        screenshot_url = row.get('screenshot_url', '').strip() or None
        tool_type = row.get('type', '').strip() or None

        # Skip rows with empty name or source
        if not name or not source:
            skipped_count += 1
            print(f"Skipping row with empty name or source: {row}")
            continue

        try:
            # Check if row exists ONLY by name and source
            cur.execute("""
                SELECT id FROM ai_tools 
                WHERE name = %s AND source = %s
            """, (name, source))
            existing_row = cur.fetchone()

            if existing_row:
                # Update existing row
                cur.execute("""
                    UPDATE ai_tools SET
                    category = %s,
                    source_url = %s,
                    short_description = %s,
                    full_description = %s,
                    screenshot_url = %s,
                    type = %s
                    WHERE name = %s AND source = %s
                """, (
                    category,
                    source_url,
                    short_description,
                    full_description,
                    screenshot_url,
                    tool_type,
                    name,
                    source
                ))
                print(f"Updated existing tool: {name} from {source}")
            else:
                # Insert new row, ignoring any source URL constraints
                cur.execute("""
                    INSERT INTO ai_tools 
                    (name, category, source, source_url, short_description, full_description, screenshot_url, type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name,
                    category,
                    source,
                    source_url,
                    short_description,
                    full_description,
                    screenshot_url,
                    tool_type
                ))
                print(f"Added new tool: {name} from {source}")

            conn.commit()
            processed_count += 1
        except psycopg2.errors.UniqueViolation:
            # If there's a unique constraint violation (e.g., on source_url)
            conn.rollback()
            duplicate_url_count += 1
            print(f"Forced insertion of tool with duplicate URL: {name} from {source}")

            # Force insert by modifying the URL slightly
            modified_source_url = f"{source_url}_{processed_count}"

            try:
                cur.execute("""
                    INSERT INTO ai_tools 
                    (name, category, source, source_url, short_description, full_description, screenshot_url, type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name,
                    category,
                    source,
                    modified_source_url,
                    short_description,
                    full_description,
                    screenshot_url,
                    tool_type
                ))
                conn.commit()
                print(f"Inserted tool with modified URL: {name}")
            except Exception as e:
                conn.rollback()
                print(f"Error force inserting {name}: {e}")
        except Exception as e:
            conn.rollback()
            print(f"Error processing {name}: {e}")

    print(f"Successfully processed {processed_count} rows")
    print(f"Skipped {skipped_count} rows")
    print(f"Handled {duplicate_url_count} rows with duplicate URLs")

    # Close connection
    cur.close()
    conn.close()


def verify_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, source, source_url, type FROM ai_tools ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    print("\nRecent entries in database:")
    for row in rows:
        print(f"ID: {row[0]} | Name: {row[1]} | Source: {row[2]} | URL: {row[3]} | Type: {row[4]}")
    cur.close()
    conn.close()


if __name__ == "__main__":
    import_csv_to_postgres()
    verify_data()