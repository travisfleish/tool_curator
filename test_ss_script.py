import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the path to your screenshots directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "backend", "static", "screenshots")

SOURCES = [
    "FutureTools.io",
    "Toolify.ai",
    "There's an AI for That",
    "AI Top Tools",
    "AI Tools Directory"
]


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


def check_screenshot_status():
    """
    Comprehensive diagnostic of tool screenshots
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch all tools
    cur.execute("""
        SELECT name, source, source_url, screenshot_url 
        FROM ai_tools 
        ORDER BY source, name
    """)
    tools = cur.fetchall()

    cur.close()
    conn.close()

    # Diagnostic variables
    total_tools = len(tools)
    tools_by_source = {}
    tools_without_screenshots = []
    tools_with_invalid_urls = []

    # Analyze each tool
    for name, source, source_url, screenshot_url in tools:
        # Group tools by source
        if source not in tools_by_source:
            tools_by_source[source] = []
        tools_by_source[source].append(name)

        # Check screenshot filename
        filename = f"{name.replace(' ', '_').lower()}.png"
        file_path = os.path.join(SCREENSHOTS_DIR, filename)

        # Diagnostic checks
        screenshot_file_exists = os.path.exists(file_path)
        screenshot_file_size = os.path.getsize(file_path) if screenshot_file_exists else 0

        # Check for tools with issues
        has_valid_screenshot = (
                screenshot_url and
                "/static/screenshots/" in screenshot_url and
                screenshot_file_exists and
                screenshot_file_size > 0
        )

        if not has_valid_screenshot:
            issue_details = {
                'name': name,
                'source': source,
                'source_url': source_url,
                'screenshot_url': screenshot_url,
                'file_exists': screenshot_file_exists,
                'file_size': screenshot_file_size
            }
            tools_without_screenshots.append(issue_details)

        # Check for invalid source URLs
        if not source_url or source_url.strip() == '':
            tools_with_invalid_urls.append(name)

    # Print comprehensive report
    print("=== TOOL SCREENSHOT DIAGNOSTIC REPORT ===")
    print(f"Total Tools: {total_tools}")

    # Print tools by source
    print("\n=== TOOLS BY SOURCE ===")
    for source, tools in tools_by_source.items():
        print(f"{source}: {len(tools)} tools")

    # Print tools without screenshots
    print("\n=== TOOLS WITHOUT VALID SCREENSHOTS ===")
    for tool in tools_without_screenshots:
        print(f"Tool: {tool['name']}")
        print(f"  Source: {tool['source']}")
        print(f"  Source URL: {tool['source_url']}")
        print(f"  Screenshot URL in DB: {tool['screenshot_url']}")
        print(f"  Screenshot File Exists: {tool['file_exists']}")
        print(f"  Screenshot File Size: {tool['file_size']} bytes")
        print("---")

    # Print tools with invalid URLs
    print("\n=== TOOLS WITH INVALID URLs ===")
    for tool in tools_with_invalid_urls:
        print(tool)

    # Summary
    print("\n=== SUMMARY ===")
    print(f"Tools without valid screenshots: {len(tools_without_screenshots)}")
    print(f"Tools with invalid URLs: {len(tools_with_invalid_urls)}")


if __name__ == "__main__":
    check_screenshot_status()