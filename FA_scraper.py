from selenium import webdriver
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import urllib3
import csv

try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found.")

file_number = 1
record_count = 0
counter = 1

options = webdriver.ChromeOptions()
#options.headless = True
options.add_argument("--window-size=1920,1200")
options.add_experimental_option("detach", True)


DRIVER_PATH = "/path/to/chromedriver"
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

driver.get("https://easy.seccom.com.my:8222/search?searchType=entity&name=d&includeInactive=false&isCMSLChecked=true&licenceRepCheck=true&marketingRepCheck=true&responsiblePersonCheck=true&registeredPersonCheck=true&identityType=1") 

# create new csv file
def create_file(number):
    global file
    global writer
    file = open(f'FA_{number}.csv', 'w', encoding='utf8', newline='')
    writer = csv.writer(file)
    # writer header rows
    writer.writerow(['Company', 'Last Name', 'Email', 'Phone', 'Website', 'Industry'])
    print("File Created")

def change_page(page):
    time.sleep(0.7)
    input_box = driver.find_element(By.ID, "txtDtCurrentPage")
    digit = str(page)
    # highlight and enter number in input box
    if len(digit) != 1:
        print("fart")
        ActionChains(driver)\
            .click(input_box)\
            .key_down(Keys.SHIFT)\
            .send_keys(Keys.ARROW_RIGHT)\
            .send_keys(Keys.ARROW_RIGHT)\
            .send_keys(Keys.ARROW_RIGHT)\
            .send_keys(Keys.ARROW_RIGHT)\
            .key_up(Keys.SHIFT)\
            .send_keys(digit[0])\
            .perform()

        time.sleep(1)
        input_2 = driver.find_element(By.ID, "txtDtCurrentPage")

        ActionChains(driver)\
            .click(input_2)\
            .send_keys(Keys.ARROW_RIGHT)\
            .send_keys(digit[1])\
            .perform()
    else:
        ActionChains(driver)\
            .click(input_box)\
            .key_down(Keys.SHIFT)\
            .send_keys(Keys.ARROW_RIGHT)\
            .send_keys(Keys.ARROW_RIGHT)\
            .send_keys(Keys.ARROW_RIGHT)\
            .send_keys(Keys.ARROW_RIGHT)\
            .key_up(Keys.SHIFT)\
            .send_keys(page)\
            .perform()


    print("on page: " + str(page))
    driver.implicitly_wait(5)

def scrape():
    global file_number, record_count, counter

    print(counter)
    change_page(counter)
    time.sleep(1)

    title = driver.find_elements(By.XPATH, "/html/body/app-root/body/app-landing-search/div/div/div[3]/div/div/cc-datatable/div/form/table/tbody/tr/td/div/a")
    companies = []

    for titles in title:
        companies.append(titles.text)
        name = titles.text
    print(companies)
    for x in companies:
        driver.find_element(By.LINK_TEXT, x).click()
        driver.implicitly_wait(20)
        contact_btn = driver.find_element(By.XPATH, "/html/body/app-root/body/app-entity-profile/div[2]/div/div/div/div[2]/div[2]/div/div/ul/li[2]/a/span")
        contact_btn.click()
        driver.implicitly_wait(5)

        company = driver.find_element(By.XPATH, "/html/body/app-root/body/app-entity-profile/div[2]/div/div/div/div[2]/div[1]/div/div[1]/div/div[2]/h4").text
        print(company)

        phone = driver.find_element(By.XPATH, "/html/body/app-root/body/app-entity-profile/div[2]/div/div/div/div[2]/div[2]/div/div/div/div[2]/ul/li/div/div/div/div/div[1]").text
        print(phone)

        email = driver.find_element(By.XPATH, "/html/body/app-root/body/app-entity-profile/div[2]/div/div/div/div[2]/div[2]/div/div/div/div[2]/ul/li/div/div/div/div/div[3]").text
        print(email)

        for link in search(company, tld = "co.in", num=1, stop=1):
            website = link
            print("Website: " + link + "\n")

        back = driver.find_element(By.LINK_TEXT, "Back to Results").click()
        change_page(counter)

        # create new file if the previous one is full
        if record_count < 999:
            print(record_count)
            writer.writerow([company, "-", email, phone, website, "Financial Advisory"])
            record_count += 1
        else:
            print(record_count)
            file.close()
            file_number += 1
            create_file(file_number)
            record_count = 0
            writer.writerow([company, "-", email, phone, website, "Financial Advisory"])

        writer.writerow([company, "-", email, phone, website, "Financial Advisory"])
        
# creating first file
create_file(file_number)

# the webpage needs a second to load the contents in
print("\nLoading page...\n")
time.sleep(0.5)

pages = driver.find_element(By.XPATH, "/html/body/app-root/body/app-landing-search/div/div/div[3]/div/div/cc-datatable/div/form/div/div/div/div[2]/div")
print("Found " + pages.text + " pages.\n")
pg_num = int(input("Enter number of pages to scrape from: "))

start = time.time()

for n in range(pg_num):
    driver.implicitly_wait(5)
    scrape()
    counter += 1
    print(str(counter) + "\n")

end = time.time()
elapsed = round(end - start, 2)

print("Time taken: " + str(elapsed) + " seconds")

driver.quit()
