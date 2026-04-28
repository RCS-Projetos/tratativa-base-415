import logging
from src.websocket.driver import Driver

class UrlAccess:
    def __init__(
        self,
        driver: Driver,
        url: str
    ):
        self.logger = logging.getLogger('url_access')
        self.url = url
        self.page = driver.page # Acessamos a página do Playwright
        
    
    def url_access(self):
        self.logger.info('Acessando URL')
        self.page.goto(self.url)
        self.check_url_access()

    def check_url_access(self):
        self.logger.info('Verificando URL')
        self.page.wait_for_url(self.url)
        self.logger.info('URL acessada com sucesso')