import os
import time
from dotenv import load_dotenv
from .functions import Login
from .selenium import Driver
from .functions.logger import Logger

load_dotenv()


class SSW:
    def __init__(self, driver: Driver, company: str, tax: str, user: str, password: str, download_dir: str = 'Downloads'):
        self.logger = Logger()
        self.tax = tax
        self.company = company
        self.user = user
        self.password = password
        self.download_dir = download_dir
        self.driver_instance = driver

    
    def driver(self):
        return self.driver_instance

    def make_login(self):
        url = 'https://sistema.ssw.inf.br/bin/ssw0422'

        self.logger.info("Realizando login")
        login = Login(self.driver_instance, self.company, self.tax, self.user, self.password, url)
        login.login()
        time.sleep(1)
        self.logger.info("Login realizado")

    def execute_report(self, **kwargs):
        self.make_login()
        data = self.report(**kwargs)
        self.close()

        if data:
            return data

    def close(self):
        time.sleep(10)
        self.driver_instance.quit()

    def report(self):
        #Altere o Report AQUI
        ...
