import requests
import psycopg2
import os
import urllib.parse
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Specific tools to process
TOOLS_TO_SCREENSHOT = [
    {
        'name': 'Klap',
        'url': 'https://klap.app/'
    },
    {
        'name': 'Humata',
        'url': 'https://www.humata.ai/'
    },
    {
        'name': 'RambleFix',
        'url': 'https://ramblefix.com/'
    },
    {
        'name': 'Saner.AI',
        'url': 'https://saner.ai/'
    },
    {
        'name': 'Adobe',
        'url': 'https://www.adobe.com/'
    },
    {
        'name': 'DeepL',
        'url': 'https://www.deepl.com/'
    },
    {
        'name': 'Miro',
        'url': 'https://miro.com/'
    },
    {
        'name': 'OpenAI',
        'url': 'https://openai.com'
    },
    {
        'name': 'Sora',
        'url': 'https://openai.com/sora/'
    }
]

# Set the path to your screenshots directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "backend", "static", "screenshots")


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


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

        print(f"Attempting to capture screenshot for {name} from {url}")

        response = requests.get(screenshot_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))

            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            img.save(save_path)
            print(f"✅ Screenshot saved for {name}")
            return f"/static/screenshots/{filename}"
        else:
            print(f"❌ Error taking screenshot for {name}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception while taking screenshot for {name}: {e}")
        return None


def update_targeted_screenshots():
    """
    Update screenshots for specific tools.
    """
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Using screenshot directory: {SCREENSHOTS_DIR}")

    # Ensure screenshot directory exists
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    conn = get_db_connection()
    cur = conn.cursor()

    for tool in TOOLS_TO_SCREENSHOT:
        name = tool['name']
        url = tool['url']

        print(f"\nProcessing {name}...")
        screenshot_path = save_screenshot(url, name)

        if screenshot_path:
            # Update the database with the new screenshot path
            cur.execute(
                "UPDATE ai_tools SET screenshot_url = %s WHERE name = %s;",
                (screenshot_path, name)
            )
            print(f"Updated database for {name}")
        else:
            print(f"Failed to update screenshot for {name}")

    conn.commit()
    cur.close()
    conn.close()

    print("\n=== Completed Screenshot Generation ===")


if __name__ == "__main__":
    update_targeted_screenshots()