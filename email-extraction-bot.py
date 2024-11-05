import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import time
from webdriver_manager.chrome import ChromeDriverManager

# Function to load URLs and names from CSV
def load_data(input_file_path):
    df = pd.read_csv('Missing_Names3.csv')
    if 'Website' in df.columns and 'Name' in df.columns:
        df = df.dropna(subset=['Website', 'Name'])
        df['Website'] = df['Website'].str.strip()
        df['Name'] = df['Name'].str.strip()
        df = df[df['Website'] != '']
        df = df.reset_index(drop=True)
        data = df[['Name', 'Website']]
        return data
    else:
        print("Error: 'Website' or 'Name' column not found.")
        return None

# Function to initialize Selenium WebDriver
def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to extract emails from HTML content
def extract_emails(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', soup.get_text()))
    return emails

# Function to navigate to common contact pages
def try_contact_pages(driver, base_url):
    contact_pages = [
        '/contact', '/contact-us', '/about', '/contact.html', '/contact-us.html'
    ]
    emails = set()
    for page in contact_pages:
        url = base_url + page
        driver.get(url)
        time.sleep(1)
        html_content = driver.page_source
        emails.update(extract_emails(html_content))
        if emails:  # Stop if emails are found
            break
    return emails

# Function to read existing emails from the CSV file
def read_existing_emails(output_file_path):
    try:
        df = pd.read_csv(output_file_path)
        if 'Email' in df.columns:
            return set(df['Email'].tolist())
    except FileNotFoundError:
        return set()
    return set()

# Function to append names, URLs, and emails to a CSV file
def append_data_to_csv(name, url, emails, output_file_path, status):
    existing_emails = read_existing_emails(output_file_path)
    new_emails = set()
    data = []

    for email in emails:
        if email not in existing_emails:
            new_emails.add(email)
            data.append((name, url, email))
    
    if data:
        df = pd.DataFrame(data, columns=['Name', 'Website', 'Email'])
        df.to_csv(output_file_path, mode='a', header=not pd.io.common.file_exists(output_file_path), index=False)
        print(f"Added {len(new_emails)} new emails to '{output_file_path}'")

    if status:
        df_status = pd.DataFrame([(name, url, status)], columns=['Name', 'Website', 'Status'])
        df_status.to_csv(output_file_path, mode='a', header=not pd.io.common.file_exists(output_file_path), index=False)
        print(f"Logged status for {name}: {status}")

# Main function to process URLs and extract emails
def process_data(input_file_path, output_file_path):
    data = load_data(input_file_path)
    if data is None or data.empty:
        print("No data to process.")
        return
    
    driver = initialize_driver()
    
    for index, row in data.iterrows():
        name = row['Name']
        url = row['Website']
        if pd.isna(url) or url == '':
            append_data_to_csv(name, 'No website link', set(), output_file_path, 'No website link')
            continue
        
        try:
            driver.get(url)
            time.sleep(1)  # Wait for the page to load (adjust as necessary)
            html_content = driver.page_source
            emails = extract_emails(html_content)
            
            # If no emails found, try common contact pages
            if not emails:
                emails = try_contact_pages(driver, url)
            
            if emails:
                append_data_to_csv(name, url, emails, output_file_path, None)
                print(f"Processed {url} for {name}, found {len(emails)} emails")
            else:
                append_data_to_csv(name, url, emails, output_file_path, 'No email found')
                print(f"Processed {url} for {name}, found no emails")
        except Exception as e:
            print(f"Failed to process {url} for {name}: {e}")
            append_data_to_csv(name, url, set(), output_file_path, 'Error occurred')
    
    driver.quit()
    print(f"All URLs processed. Emails saved to '{output_file_path}'")

# Call the main function
input_path = 'Missing_Names3.csv'  # Update this with the path to your raw data file
output_path = 'EMAIL.csv'  # Update this with the path to your output file
process_data(input_path, output_path)
