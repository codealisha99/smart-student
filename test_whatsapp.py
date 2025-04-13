import os
import time
import logging
from openai import OpenAI

client = OpenAI()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from openai import OpenAI

client = OpenAI()

# def ask_openai(prompt):
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "user", "content": prompt}
#         ]
#     )
#     return response.choices[0].message.content.strip()



GROUP_NAME = "Abhijitam Dubey"
TRIGGERS = ["assignment", "form", "experiment", "submit", "project"]

def setup_driver():
    options = Options()
    options.add_argument("--user-data-dir=./chrome_data")
    options.add_argument("--profile-directory=Default")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def wait_for_element(driver, xpath, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))

def go_to_group(driver, group_name):
    try:
        print(f"🔍 Searching for group: {group_name}")

        # Wait for and find the search input
        search_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        search_box.clear()
        time.sleep(1)
        search_box.send_keys(group_name)
        time.sleep(3)  # Let results load

        # Grab all chat titles
        chat_titles = driver.find_elements(By.XPATH, '//span[@title]')
        found = False
        for chat in chat_titles:
            title = chat.get_attribute("title")
            print(f"📋 Found chat title: {title}")
            if group_name.lower() in title.lower():
                chat.click()
                found = True
                print(f"✅ Group '{title}' opened.")
                break

        if not found:
            raise Exception(f"No group found matching: {group_name}")

    except Exception as e:
        import logging
        logging.error(f"Error going to group {group_name}: {e}")



def get_recent_messages(driver, limit=15):
    xpath = '//div[contains(@class, "message-in")]//span[contains(@class,"selectable-text")]'
    messages = driver.find_elements(By.XPATH, xpath)
    return [msg.text for msg in messages[-limit:]]

def extract_tasks(messages):
    tasks = []
    for msg in messages:
        if any(trigger in msg.lower() for trigger in TRIGGERS):
            tasks.append(msg.strip())
    return tasks

def ask_openai(task):
    prompt = f"Provide a summary and study material for this college task: {task}"
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

def display_todo(tasks):
    print("\n📌 To-Do List:\n")
    for i, task in enumerate(tasks, 1):
        print(f"[ ] {task}")
        print(f"📚 Material:\n{ask_openai(task)}\n")

def main():
    driver = setup_driver()
    driver.get("https://web.whatsapp.com")
    print("✅ WhatsApp Web opened! Please scan the QR code.")

    input("🔓 After chats load, press Enter to continue...")

    go_to_group(driver, GROUP_NAME)
    messages = get_recent_messages(driver)
    tasks = extract_tasks(messages)

    if tasks:
        display_todo(tasks)
    else:
        print("✅ No new tasks found.")

    input("Press Enter to quit...")
    driver.quit()


if __name__ == "__main__":
    main()
