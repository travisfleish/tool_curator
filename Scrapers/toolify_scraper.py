import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import psycopg2
import os
from dotenv import load_dotenv
import time

# Load environment variables
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
            source TEXT,
            source_url TEXT UNIQUE
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()


# Function to scrape Toolify.ai New Tools page
def scrape_toolify():
    url = "https://www.toolify.ai/new"

    # Set up Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    chrome_options.add_argument("--headless")  # Run in headless mode for efficiency
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    print("[INFO] Opening Toolify.ai New Tools page in Chrome...")
    driver.get(url)

    tools = []

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tool-item"))
        )
        print("[INFO] AI tools have loaded.")
    except Exception as e:
        print("[ERROR] Timeout waiting for AI tool elements:", e)
        driver.quit()
        return []

    # Find all tool elements
    tool_cards = driver.find_elements(By.CLASS_NAME, "tool-item")

    for card in tool_cards:
        try:
            # Extract tool name
            name_element = card.find_element(By.CLASS_NAME, "go-tool-detail-name")
            name = name_element.text.strip()

            # Extract short description
            short_description_element = card.find_element(By.CLASS_NAME, "tool-desc")
            short_description = short_description_element.text.strip()

            # Extract the actual AI tool URL (ensuring it is NOT a Toolify.ai URL)
            actual_tool_url = ""

            try:
                # First attempt: Extract external URLs, skipping any Toolify.ai links
                tool_links = card.find_elements(By.XPATH, './/a[@rel="dofollow" and @target="_blank"]')

                for link in tool_links:
                    url = link.get_attribute("href")
                    if "toolify.ai" not in url:  # Ensure it's NOT a Toolify.ai internal link
                        actual_tool_url = url
                        break  # Stop searching once we find a valid external link

            except:
                actual_tool_url = ""  # If no valid link is found, leave it empty

            # Append extracted data
            tools.append((name, short_description, "Toolify.ai", actual_tool_url))

        except Exception as e:
            print(f"[ERROR] Skipping a tool due to an error: {e}")
            continue

    driver.quit()

    # Print extracted tools
    print("[INFO] Extracted Tools:")
    for tool in tools:
        print(tool)

    return tools


# Function to store data in PostgreSQL
def store_data(tools):
    conn = connect_db()
    cur = conn.cursor()

    for tool in tools:
        cur.execute(
            "INSERT INTO ai_tools (name, short_description, source, source_url) VALUES (%s, %s, %s, %s) ON CONFLICT (source_url) DO NOTHING",
            tool
        )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    create_table()
    tools = scrape_toolify()
    store_data(tools)
    print(f"[INFO] Scraped and stored {len(tools)} AI tools from Toolify.ai New Tools!")
