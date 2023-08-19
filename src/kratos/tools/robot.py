import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service


from kratos.tools.logger import Logger

class Robot():
    def __init__(self) -> None:
        self.logger = Logger()
        self.options = self.__init_options()
        self.driver = self.__init_driver()

    def check_element_by_tag_name(self, parent, name):
        try:
            parent.find_element(By.TAG_NAME, name)
        except Exception as e:
            return False
        return True
    
    def check_element_by_class_name(self, parent, name):
        try:
            parent.find_element(By.CLASS_NAME, name)
            return True
        except Exception as e:
            return False
        
    def check_element_by_id(self, parent, name):
        try:
            parent.find_element(By.ID, name)
            return True
        except Exception as e:
            return False
        
    def headless(self, value:bool):
        try:
            if value:
                self.options.add_argument("--headless")
            else:
                self.options.arguments.remove("--headless")
        except Exception as e:
            raise e

    def __init_driver(self):
        try:
            service = Service(executable_path="/usr/local/bin/geckodriver", log_output=os.path.dirname(os.path.abspath('logs')) + "/logs/geckodriver.log")
            driver = webdriver.Firefox(options=self.options, service=service)
            driver.maximize_window()

            self.logger.info(f"Driver initialization success")
            return driver
        except Exception as e:
            self.logger.error(f"An error occured with the driver initialization : {e}")
            return False

    def __init_options(self):
        try:
            options = FirefoxOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            return options
        except Exception as e:
            self.logger.error(f"An error occured with the options initialization : {e}")
            return False
        