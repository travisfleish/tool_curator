import requests
import os
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the path to your screenshots directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "backend", "static", "screenshots")

# Tool details
TOOL_NAME = "ReconXi"
TOOL_URL = "https://www.reconxi.com/"  # URL for ReconXi


def get_tool_url_from_db():
    """
    This is a placeholder function. In a real implementation, you would:
    1. Connect to your database
    2. Query for ReconXi's URL
    3. Return the URL

    Since we don't have the actual database connection details for just ReconXi,
    you'll need to modify this or manually set the TOOL_URL above.
    """
    # For demonstration - either implement database connection or set TOOL_URL manually
    print("In a real implementation, this would query the database for ReconXi's URL")
    return None


def save_screenshot(url, name):
    """
    Save a screenshot for ReconXi.

    Args:
        url (str): URL of ReconXi
        name (str): Name of the tool (ReconXi)

    Returns:
        str or None: Path to saved screenshot, or None if failed
    """
    try:
        filename = f"{name.replace(' ', '_').lower()}.png"
        save_path = os.path.join(SCREENSHOTS_DIR, filename)

        if not url or url.strip() == "":
            print(f"No URL provided for {name}, cannot take screenshot.")
            return None

        api_key = os.getenv("SCREENSHOTONE_API_KEY")
        if not api_key:
            print("SCREENSHOTONE_API_KEY not found in environment variables")
            return None

        screenshot_url = f"https://api.screenshotone.com/take?access_key={api_key}&url={url}&viewport_width=1280&viewport_height=800&format=png"

        print(f"Taking screenshot of {url}...")
        response = requests.get(screenshot_url)

        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))

            # Ensure the directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            img.save(save_path)
            print(f"Screenshot saved to {save_path}")
            return f"/static/screenshots/{filename}"
        else:
            print(f"Error taking screenshot: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Exception while taking screenshot: {e}")
        return None


def update_reconxi_screenshot():
    """
    Takes a screenshot of ReconXi and updates its screenshot URL in the database.
    """
    print("Starting ReconXi screenshot update...")

    # Ensure screenshot directory exists
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    # Get ReconXi URL - either from database or use the one defined at the top
    url = TOOL_URL or get_tool_url_from_db()

    if not url:
        print("ERROR: No URL available for ReconXi. Please set TOOL_URL in the script.")
        return

    print(f"Generating screenshot for {TOOL_NAME} ({url})...")
    screenshot_path = save_screenshot(url, TOOL_NAME)

    if screenshot_path:
        print(f"🖼️ Successfully saved screenshot: {screenshot_path}")
        print(f"To update the database, you would run:")
        print(f"UPDATE ai_tools SET screenshot_url = '{screenshot_path}' WHERE name = '{TOOL_NAME}';")
    else:
        print(f"❌ Failed to generate screenshot for {TOOL_NAME}")


if __name__ == "__main__":
    update_reconxi_screenshot()