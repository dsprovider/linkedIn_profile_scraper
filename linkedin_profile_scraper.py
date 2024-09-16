# Imported Libraries
import os
import time
import random
import requests

import pandas as pd

from bs4 import BeautifulSoup
from user_agents import parse
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============= Generic Auxiliary Functions ===========================================================================================

def remove_empty_lines(input_string):
    lines = input_string.split('\n')
    non_empty_lines = [line for line in lines if line.strip() != '']
    return '\n'.join(non_empty_lines)

# ============= Request Functions ===========================================================================================
   
def sleep_for_random_duration(min_duration=3, max_duration=6):
    sleep_duration = random.uniform(min_duration, max_duration)
    print(f">> Sleeping for {sleep_duration:.2f} seconds...")
    time.sleep(sleep_duration)

def get_random_user_agent():
    ua = UserAgent()
    return ua.random

def send_request(url):
    user_agent = get_random_user_agent()
    headers = {'User-Agent': user_agent}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        return response
    except requests.RequestException as e:
        print(">> Error:", e)
        return None

def get_pc_user_agent():
    ua = UserAgent()
    while True:
        random_user_agent = ua.random
        if parse(random_user_agent).is_pc:
            return random_user_agent

# ============= Setup Functions ===============================================================================================

def setup_driver():
    # ua = UserAgent()
    random_user_agent = get_pc_user_agent()    

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument(f'user-agent={random_user_agent}')
    chrome_options.add_argument("--window-size=1500,800")

    # Start the WebDriver and initiate a new browser session
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# ============= Processing Functions ==========================================================================================

def accept_cookies_prompt(driver):
    try:
        # Wait for the cookie prompt to appear
        cookie_prompt = WebDriverWait(driver, 6).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "artdeco-global-alert.artdeco-global-alert--NOTICE.artdeco-global-alert--COOKIE_CONSENT"))
        )

        # Find the accept button and click on it
        accept_button = driver.find_element(By.CLASS_NAME, "artdeco-global-alert-action.artdeco-button.artdeco-button--inverse.artdeco-button--2.artdeco-button--primary")
        if accept_button:
            accept_button.click()

        print(">> Accepted the cookie prompt!")

    except Exception as e:
        print(">> Error occurred while waiting for or handling the cookie prompt:", e)


def login_to_linkedin(driver):
    email = "xxx139637@gmail.com"
    passwd = "2kSD#&ilXt-Nu32"

    # email = "felix.carter.tech@gmail.com"
    # passwd = "FakeDummyLDAccount@@"

    try:
        driver.get("https://www.linkedin.com/login")
        sleep_for_random_duration(3, 4)

        # -- (0) -- Cookies Prompt
        accept_cookies_prompt(driver)
        sleep_for_random_duration(3, 4)

        # -- (1) -- Enter credentials
        input_email = driver.find_element(By.ID, 'username')
        if input_email:
            input_email.send_keys(email)
            sleep_for_random_duration(3, 4)

        input_passwd = driver.find_element(By.ID, 'password')
        if input_passwd:
            input_passwd.send_keys(passwd)
            sleep_for_random_duration(3, 4)

        # -- (2) -- Sign In
        sign_in_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-litms-control-urn="login-submit"]')
        if sign_in_btn:
            sign_in_btn.click()
            sleep_for_random_duration(20, 25) # Security Verification Check
            # sleep_for_random_duration(5, 6)

    except Exception as e:
        print(f">> Error occurred. {type(e)}")
    

# ============= Site Functions ===============================================================================================   

def parse_linkedin_profile(profile_url, driver):
    try:
        driver.get(profile_url)
        sleep_for_random_duration(5, 6)

        main_element = driver.find_element(By.CLASS_NAME, 'scaffold-layout__main')
        if main_element:
            
            # --- [A] --- Name ------
            h1_elem = main_element.find_element(By.CLASS_NAME, 'text-heading-xlarge.inline.t-24.v-align-middle.break-words')
            if h1_elem:
                name = h1_elem.text

            # --- [B] --- Profession ------
            profession_div = main_element.find_element(By.CLASS_NAME, 'text-body-medium.break-words')
            if profession_div:
                profession = profession_div.text
                
            # --- [C] --- Connections ------
            connections_div = main_element.find_element(By.CLASS_NAME, 'hrvgBtWSbhpGHHryftWDXAKDSnnrcfdauTh.kHWbXYtvsgMSuhyZreQxvuRJwOzWwzZeiolo')
            if connections_div:
                connections = connections_div.text

            # --- [D] --- About Me ------
            about_me_div = main_element.find_element(By.CLASS_NAME, 'qNEOAnyGVGzbPxDAcvLdXUmhrlUWIjJCBwMQ.full-width')
            if about_me_div:
                about_me_inner_htmtl = about_me_div.get_attribute('innerHTML')
                about_me_soup = BeautifulSoup(about_me_inner_htmtl, 'html.parser')
                about_me_text = about_me_soup.get_text()

            # --- [E] --- Education ------
            education_url = profile_url + 'details/education/'
            driver.get(education_url)
            sleep_for_random_duration(5, 6)

            education_main = driver.find_element(By.CLASS_NAME, 'scaffold-layout__main')
            if education_main:
                education_section = education_main.find_element(By.TAG_NAME, 'section')
                if education_section:
                    education_ul = education_section.find_element(By.CLASS_NAME, 'gTHfrqEnfeOVEzKROdubmOZByDzJwJCxRPfgeik ')
                    if education_ul:
                        education_inner_html = education_ul.get_attribute('innerHTML')
                        education_soup = BeautifulSoup(education_inner_html, 'html.parser')
                        education_text = remove_empty_lines(education_soup.get_text())

            print(f"[+] Candidate: {name}")
            print(f"[+] Profession: {profession}")
            print(f"[+] Connections: {connections}")
            print(f"[+] About me: {about_me_text}")
            print(f"[+] Education: {education_text}")

    except Exception as e:
        print(f">> Error while scraping URL: '{profile_url}'")

# ============= Site Scrapers ================================================================================================



# =============================================================================================================================

def main():
    
    # Profiles file
    input_file = os.path.join(os.getcwd(), 'profiles.xlsx')

    # Set up driver
    driver = setup_driver()
    login_to_linkedin(driver)

    # Iterate over the 'profileURL' column
    df = pd.read_excel(input_file)
    for url in df['profileURL']:
        try:
            parse_linkedin_profile(url, driver)

        except Exception as e:
            print(f">> Error occurred. {type(e)}")
    
    driver.quit()
    

if __name__ == "__main__":
    main()
