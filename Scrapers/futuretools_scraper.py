import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import psycopg2
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL connection settings
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}


# Function to connect to PostgreSQL
def connect_db():
    return psycopg2.connect(**DB_CONFIG)


# Function to create table if it doesn't exist
def create_table():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS ai_tools (
            id SERIAL PRIMARY KEY,
            name TEXT,
            short_description TEXT,
            full_description TEXT,
            category TEXT,
            source TEXT,
            source_url TEXT UNIQUE
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()


# Function to get the actual tool URL by following the redirect
def get_final_url(redirect_url):
    try:
        response = requests.get(redirect_url, allow_redirects=True, timeout=10)
        return response.url  # This is the actual AI tool website
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to follow redirect for {redirect_url}: {e}")
        return redirect_url  # Fall back to original if error occurs


# Function to scrape FutureTools.io Newly Added page
def scrape_futuretools():
    url = "https://www.futuretools.io/newly-added"

    # Set up Selenium WebDriver (no headless mode so you can see it)
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    print("[INFO] Opening FutureTools.io Newly Added page in Chrome...")
    driver.get(url)

    tools = []

    for i in range(5):  # Limit to first 5 tools
        # Refresh the page before each iteration to avoid stale elements
        driver.get(url)
        time.sleep(3)  # Allow time for page reload

        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tool-item-columns-new"))
            )
            print("[INFO] AI tools have loaded.")
        except Exception as e:
            print("[ERROR] Timeout waiting for AI tool elements:", e)
            driver.quit()
            return []

        # Find fresh elements
        tool_cards = driver.find_elements(By.CLASS_NAME, "tool-item-columns-new")
        if i >= len(tool_cards):
            print("[INFO] No more tools found.")
            break

        try:
            card = tool_cards[i]
            name_element = card.find_element(By.CLASS_NAME, "tool-item-link---new")
            name = name_element.text.strip()

            short_description_element = card.find_element(By.CLASS_NAME, "tool-item-description-box---new")
            short_description = short_description_element.text.strip()

            category_element = card.find_element(By.CLASS_NAME, "link-block-7")
            category = category_element.text.strip() if category_element else "Unknown"

            tool_page_link_element = card.find_element(By.CLASS_NAME, "tool-item-link-block---new")
            tool_page_url = tool_page_link_element.get_attribute("href")

            driver.get(tool_page_url)
            print(f"[INFO] Scraping tool page: {tool_page_url}")

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "link-block-2"))
            )

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Extract the redirect URL
            redirect_url_tag = soup.find("a", class_="link-block-2")
            redirect_url = redirect_url_tag["href"] if redirect_url_tag else ""

            # Follow the redirect to get the actual AI tool URL
            actual_tool_url = get_final_url(redirect_url) if redirect_url else ""

            # Extract full description
            full_description_tag = soup.find("div", class_="rich-text-block w-richtext")
            full_description = full_description_tag.text.strip() if full_description_tag else short_description

            tools.append((name, short_description, full_description, category, "FutureTools.io", actual_tool_url))

        except Exception as e:
            print(f"[ERROR] Skipping a tool due to an error: {e}")
            continue

    driver.quit()

    # Print extracted tools
    print("Extracted Tools:")
    for tool in tools:
        print(tool)

    return tools


# Function to store data in PostgreSQL
def store_data(tools):
    conn = connect_db()
    cur = conn.cursor()

    for tool in tools:
        cur.execute(
            "INSERT INTO ai_tools (name, short_description, full_description, category, source, source_url) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (source_url) DO NOTHING",
            tool
        )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    create_table()
    tools = scrape_futuretools()
    store_data(tools)
    print(f"Scraped and stored {len(tools)} AI tools from FutureTools.io Newly Added!")
