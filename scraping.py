from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

input_selector = 'searchboxinput'
open_review_selector = 'button.HHrUdb.fontTitleSmall.rqjGif'
review_container_selector = "div.jJc9Ad"
more_button_selector = "button.w8nwRe.kyuRq"
comment_selector = "span.wiI7pd"
reply_selector = "div.wiI7pd"
review_text_selector = "div.jftiEf.fontBodyMedium"
review_list_container_selector = "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde"
review_list = []

MAX_REVIEW_NUMBER = 50

# put the name here
PLACE_NAME = ""


def process_review_container(div_element, index):

    comment_selector = "span.wiI7pd"

    try: 
        # Wait for the button to be clickable within the div element
        WebDriverWait(div_element, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, more_button_selector)))
        
        # Click the More button
        buttons = div_element.find_elements(By.CSS_SELECTOR, more_button_selector)
        if len(buttons) > 0:
            for b in buttons:
                b.click()

        comment = div_element.find_element(By.CSS_SELECTOR, comment_selector).text
        reply = div_element.find_element(By.CSS_SELECTOR, reply_selector).text

        review_list.append({
            'comment': comment,
            'reply': reply
        })

        print(f"{index}. Comment and reply are added!")

    except:
        print(f"{index}. No reply")
    finally:
        return
    

def get_google_maps_reviews(place_name):
    # Setup WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:

        # Open Google Maps
        driver.get('https://www.google.com/maps')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, input_selector)))

        
        # Search for the place
        search_box = driver.find_element(By.ID, input_selector)
        search_box.send_keys(place_name)
        search_box.send_keys(Keys.ENTER)

        # Click on review
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, open_review_selector)))
        first_result = driver.find_element(By.CSS_SELECTOR, open_review_selector)
        first_result.click()

        page = 1

        while (True):
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, review_text_selector)))
            reviews = driver.find_elements(By.CSS_SELECTOR, review_text_selector)
            last_10_reviews = reviews[-10:] if len(reviews) >= 10 else reviews

            index = 1
            for r in last_10_reviews:
                count = (page - 1)*10 + index
                process_review_container(r, count)
                index = index + 1
                if count == MAX_REVIEW_NUMBER:
                    return

            # scroll to bottom of review_list_container_selector
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", driver.find_element(By.CSS_SELECTOR, review_list_container_selector))
            time.sleep(2)  # wait for new reviews to load

            page = page + 1

    finally:
        # Close the driver
        driver.quit()
        return

if __name__ == "__main__":
    get_google_maps_reviews(PLACE_NAME)

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(review_list)

    # Save the DataFrame to an Excel file
    try:
        df.to_excel(f'{PLACE_NAME}_{len(review_list)}.xlsx', index=False)
        print("Xlsx file created")
    except:
        print("Failed to create xlsx file")
