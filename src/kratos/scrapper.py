import os
import time

from decouple import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
import json
import unicodedata

from kratos.tools.logger import Logger


class Kratos():

    def __init__(self) -> None:
        self.logger = Logger()
        self.driver = self.__init_scrapper()

    def carrefour(self):
        """
            Carrefour site scrapper
        """
        try:
            # Launch Carrefour product home page
            self.driver.get("https://www.carrefour.fr/r")
            time.sleep(5) # Sleep 5 seconds

            # WebDriverWait is waiting for the element to appear
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "onetrust-reject-all-handler"))
            )

            # Send a keybord key press action to the element
            element.send_keys(Keys.RETURN)
            # Sleep 2 seconds
            time.sleep(2) 

            # Get the div where all the product categories is located
            category_elements = self.driver.find_elements(By.CLASS_NAME, "ds-carousel__item")[2:] # [2:] To exclude Promotion pages
            
            # Create category list
            categories = []
            
            # Loop through category_elements list
            for item in category_elements:
                # Get category element link 
                link = item.find_element(By.CLASS_NAME, 'tagline__picker')
                # Get category element title content  
                title = self.__delete_accent(link.find_element(By.CLASS_NAME, 'tagline__label').text)
                # get category element link content
                href = link.get_attribute('href')
                # Create category element slug
                slug = self.__slugify(title)
                # Append category object to category list
                categories.append({
                    "title" : title,
                    "slug" : slug,
                    "link": href
                })

            # Loop through all category previously extracted
            for i, sub_item in enumerate(categories):
                # Get The precise category
                cat = categories[i]
                print(f" -------------------- Category | {cat['title']} --------------------")
                # Switch to a new window
                self.driver.switch_to.new_window('tab')
                # Launch link in the new window
                self.driver.get(sub_item['link'])
                # Sleep 3 second
                time.sleep(3)
                
                # Get the container where all the sub category is displayed
                sub_container = self.driver.find_element(By.ID, "data-tags-sous-rayons")
                # get All sub category item
                sub_category_elements = sub_container.find_elements(By.CLASS_NAME, "ds-carousel__item")
                
                # Create sub category list
                sub_categories = []

                # Loop through all sub category previously extracted
                for x, sub_cat in enumerate(sub_category_elements):
                    # Get sub category element link
                    sub_link = sub_cat.find_element(By.CLASS_NAME, 'tagline__picker')
                    # Get sub category element title content
                    sub_title = self.__delete_accent(sub_link.find_element(By.CLASS_NAME, 'tagline__label').text)
                    # Get sub category element link content
                    sub_href = sub_link.get_attribute('href')
                    # Create sub category element slug
                    sub_slug = self.__slugify(sub_title)
                    # Append sub category object to sub category list
                    sub_categories.append({
                        "number": x,
                        "title" : sub_title,
                        "slug" : sub_slug,
                        "link": sub_href
                    })


                # Loop through all sub categories element
                for w, product in enumerate(sub_categories):
                    # Switch to a new window
                    self.driver.switch_to.new_window('tab')
                    # Launch link in the new window
                    self.driver.get(product['link'])
                    # Sleep 3 seconds
                    time.sleep(3)

                    # Get sub category page footer element (this element is where the "show more" button is located) 
                    footer = self.driver.find_element(By.ID, "data-voir-plus")
                    
                    # Execute script while the button element still displayed
                    while self.__check_element_by_tag_name(footer.find_element(By.CLASS_NAME, "pagination__button-wrap"), 'button'):
                        # Get button element
                        button = footer.find_element(By.CLASS_NAME, "pagination__button-wrap").find_element(By.TAG_NAME, 'button')
                        # Send a keybord key press action to the button element
                        button.send_keys(Keys.RETURN)
                        # Sleep 4 seconds
                        time.sleep(4)
                    
                    # Extract product container
                    product_container = self.driver.find_element(By.ID, 'data-plp_produits')
                    # Get all product items element
                    product_list = product_container.find_elements(By.CLASS_NAME, 'product-grid-item')

                    print(f" --------- Sub Category [{product['title']}]")
                    print(f" ________ Product list size : {len(product_list)} ________ ")
                    # Create product item list
                    items = []

                    # Loop through all product elements
                    for m, rprod in enumerate(product_list):
                        if self.__check_element_by_class_name(rprod, "main-vertical--top"):
                            # Get product element link
                            product_link_href = rprod.find_element(By.CLASS_NAME, "main-vertical--top").find_element(By.TAG_NAME, "a")
                            # Get product element title
                            product_title = rprod.find_element(By.CLASS_NAME, "product-card-title__text").text
                            # Append product object to product list
                            items.append({
                                "number" : m,
                                "title":  product_title,
                                "link" : product_link_href.get_attribute('href')
                            })
                            print(f"Product : {product_title}")
                    
                    sub_categories[w]['items'] = items

                # Affect sub categories to the respective category
                cat['sub_cat'] = sub_categories

            # Get json file link
            data_link = os.path.dirname(os.path.abspath('data')) + "/data/carrefour/categories.json"
            
            # Create JSON file to store categories, sub categories and product link
            with open(data_link, "w") as outfile:
                json.dump(categories, outfile, indent=4)
            
            # Sleep 2 seconds
            time.sleep(2)
            # Quit scrapper
            self.driver.quit()
        except Exception as e:
            # Trigger log for any exceptions
            self.logger.error(f"Carrefour scrapping process : {e}")

    def __check_element_by_tag_name(self, parent, name):
        try:
            parent.find_element(By.TAG_NAME, name)
        except Exception as e:
            return False
        return True
    
    def __check_element_by_class_name(self, parent, name):
        try:
            parent.find_element(By.CLASS_NAME, name)
            return True
        except Exception as e:
            return False
        
    def __slugify(self, s):
        s = re.sub(r'[^\w\s-]', '', s)
        s = re.sub(r'[\s_-]+', '-', s)
        s = re.sub(r'^-+|-+$', '', s)
        s = s.lower().strip()
        s = self.__delete_accent(s)
        return s

    def __delete_accent(self, text):
        text = unicodedata.normalize('NFKD', text)
        return "".join([c for c in text if not unicodedata.combining(c)]) 

    def __init_scrapper(self):
        try:
            options = FirefoxOptions()
            service = Service(executable_path="/usr/local/bin/geckodriver", log_output=os.path.dirname(os.path.abspath('logs')) + "/logs/geckodriver.log")
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            if config('HEADLESS', default=False, cast=bool):
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options, service=service)
            driver.maximize_window()

            return driver
        except Exception as e:
            self.logger.error(f"An error occured with the scrapper initialization : {e}")
