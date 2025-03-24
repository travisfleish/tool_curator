import requests
import psycopg2
import os
import urllib.parse
from PIL import Image
from io import BytesIO
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

FILTERS = ["new"]


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


def screenshot_exists(tool_name):
    """
    Check if a screenshot exists for a given tool name.

    Args:
        tool_name (str): Name of the tool to check

    Returns:
        bool: True if screenshot exists and is not empty, False otherwise
    """
    # Convert tool name to screenshot filename
    filename = f"{tool_name.replace(' ', '_').lower()}.png"
    file_path = os.path.join(SCREENSHOTS_DIR, filename)

    # Check if file exists and is not empty
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0


def get_tools_without_screenshots():
    """
    Retrieve tools that do not have existing screenshots.

    Returns:
        list: Tools without screenshots
    """
    conn = get_db_connection()
    cur = conn.cursor()

    displayed_tools = []

    for source in SOURCES:
        cur.execute(
            """
            SELECT name, source_url
            FROM ai_tools 
            WHERE source = %s
            """,
            (source,)
        )

        all_tools = cur.fetchall()
        displayed_tools.extend(all_tools[:8])

    cur.close()
    conn.close()

    # Filter out tools that already have screenshots
    tools_without_screenshots = [
        tool for tool in displayed_tools
        if not screenshot_exists(tool[0])
    ]

    return tools_without_screenshots


def save_screenshot(url, name):
    """
    Save a screenshot for a given tool.

    Args:
        url (str): URL of the tool
        name (str): Name of the tool

    Returns:
        str or None: Path to saved screenshot, or None if failed
    """
    try:
        filename = f"{name.replace(' ', '_').lower()}.png"
        save_path = os.path.join(SCREENSHOTS_DIR, filename)

        if not url or url.strip() == "":
            print(f"No URL provided for {name}, skipping...")
            return None

        api_key = os.getenv("SCREENSHOTONE_API_KEY")
        screenshot_url = f"https://api.screenshotone.com/take?access_key={api_key}&url={url}&viewport_width=1280&viewport_height=800&format=png"

        response = requests.get(screenshot_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))

            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            img.save(save_path)
            return f"/static/screenshots/{filename}"
        else:
            print(f"Error taking screenshot: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception while taking screenshot: {e}")
        return None


def update_displayed_screenshot_urls():
    """
    Update screenshot URLs for tools without existing screenshots.
    """
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Using screenshot directory: {SCREENSHOTS_DIR}")

    # Ensure screenshot directory exists
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    # Get tools that need screenshots
    tools_to_process = get_tools_without_screenshots()

    print(f"Found {len(tools_to_process)} tools without screenshots")

    conn = get_db_connection()
    cur = conn.cursor()

    for name, url in tools_to_process:
        print(f"Generating screenshot for {name} ({url})...")
        screenshot_path = save_screenshot(url, name)

        if screenshot_path:
            print(f"🖼️ Saved Screenshot: {screenshot_path}")
            cur.execute(
                "UPDATE ai_tools SET screenshot_url = %s WHERE source_url = %s;",
                (screenshot_path, url),
            )
        else:
            print(f"❌ Failed to generate screenshot for {name}")

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    update_displayed_screenshot_urls()