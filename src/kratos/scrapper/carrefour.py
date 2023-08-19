import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import json

from kratos.tools.robot import Robot
from kratos.tools.utils import slugify, delete_accent


class Carrefour(Robot):

    def __init__(self) -> None:
       super().__init__()
       self.cat_link = os.path.dirname(os.path.abspath('data')) + "/data/carrefour/categories.json"
       self.product_link = os.path.dirname(os.path.abspath('data')) + "/data/carrefour/products.json"
       self.site_link = "https://www.carrefour.fr/r"
       self.categories = self.__init_categories()

    def extract_all_products(self, output=None):
        try:
            if not os.path.getsize(self.product_link) > 0:
                # Loop through all sub categories element
                products = []
                for category in self.categories:
                    # Launch link in the new window
                    self.driver.get(category['link'])
                    # Sleep 3 seconds
                    time.sleep(3)

                    if  self.check_element_by_id(self.driver, "onetrust-reject-all-handler"):
                        element = self.driver.find_element(By.ID, "onetrust-reject-all-handler")
                        element.send_keys(Keys.RETURN)
                        time.sleep(2)

                    # Check if page is a product page with a see more button
                    if not self.check_element_by_id(self.driver, 'data-voir-plus'):
                        continue

                    # Get sub category page footer element (this element is where the "show more" button is located) 
                    footer = self.driver.find_element(By.ID, "data-voir-plus")
                    
                    # Execute script while the button element still displayed
                    while self.check_element_by_tag_name(footer.find_element(By.CLASS_NAME, "pagination__button-wrap"), 'button'):
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

                    print(f" --------- Sub Category [{category['title']}] ")
                    print(f" Product list size : {len(product_list)} ")

                    # Loop through all product elements
                    for m, rprod in enumerate(product_list):
                        if self.check_element_by_class_name(rprod, "main-vertical--top"):
                            # Get product element link
                            product_link_href = rprod.find_element(By.CLASS_NAME, "main-vertical--top").find_element(By.TAG_NAME, "a")
                            # Get product element title
                            product_title = rprod.find_element(By.CLASS_NAME, "product-card-title__text").text
                            # Append product object to product list
                            products.append({
                                "number" : m,
                                "title":  product_title,
                                "link" : product_link_href.get_attribute('href')
                            })
                self.driver.close()
                with open(self.product_link, 'w') as f:
                    json.dump(products,f)
                return products
            with open(self.product_link) as user_file:
                parsed_json = json.load(user_file)
            return parsed_json
        except Exception as e:
            # Trigger log for any exceptions
            self.logger.error(f"Carrefour - Extract all product process : {e}")

    def extract_products_from_category(self, name, output=None):
        pass

    def __init_categories(self):
        try:
            if not os.path.getsize(self.cat_link) > 0:
                # Launch Carrefour product home page
                self.driver.get(self.site_link)
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
                parent_categories = []

                # Loop through category_elements list
                for item in category_elements:
                    # Get category element link 
                    link = item.find_element(By.CLASS_NAME, 'tagline__picker')
                    # get category element link content
                    href = link.get_attribute('href')
                    # Append category object to category list
                    parent_categories.append({
                        "link": href
                    })
                
                # Create category list
                categories=[]

                # Loop through all category previously extracted
                for sub_item in parent_categories:
                    # Launch link in the new window
                    self.driver.get(sub_item['link'])
                    # Sleep 3 second
                    time.sleep(3)
                    
                    # Get the container where all the sub category is displayed
                    sub_container = self.driver.find_element(By.ID, "data-tags-sous-rayons")
                    # get All sub category item
                    sub_category_elements = sub_container.find_elements(By.CLASS_NAME, "ds-carousel__item")

                    # Loop through all sub category previously extracted
                    for x, sub_cat in enumerate(sub_category_elements):
                        # Get sub category element link
                        sub_link = sub_cat.find_element(By.CLASS_NAME, 'tagline__picker')
                        # Get sub category element title content
                        sub_title = delete_accent(sub_link.find_element(By.CLASS_NAME, 'tagline__label').text)
                        # Get sub category element link content
                        sub_href = sub_link.get_attribute('href')
                        # Create sub category element slug
                        sub_slug = slugify(sub_title)
                        # Append sub category object to sub category list
                        categories.append({
                            "title" : sub_title,
                            "slug" : sub_slug,
                            "link": sub_href
                        })

                self.driver.close()
                with open(self.cat_link, 'w') as f:
                    json.dump(categories,f)

                return categories
            with open(self.cat_link) as user_file:
                parsed_json = json.load(user_file)
            return parsed_json
        except Exception as e:
            # Trigger log for any exceptions
            self.logger.error(f"Carrefour categories initialization process : {e}")
