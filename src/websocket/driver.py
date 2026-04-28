import os
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import logging


class Driver:
    def __init__(self, headless: bool = True, download_dir: str = 'Downloads'):
        self.logger = logging.getLogger('driver_websockets')
        self.logger.info(f'Iniciando Driver com headless={headless} e download_dir={download_dir}')
        
        self.download_dir = os.path.abspath(download_dir)
        self._ensure_download_dir()
        
        self.playwright = sync_playwright().start()
        
        self.browser: Browser = self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        self.context: BrowserContext = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            accept_downloads=True # Habilita downloads
        )

        self.page: Page = self.context.new_page()
        
    def _ensure_download_dir(self):
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            self.logger.info(f'Directory {self.download_dir} created')
    
    def get(self, url: str):
        self.logger.info(f'Acessando {url}')
        self.page.goto(url, wait_until='domcontentloaded')
    
    def quit(self):
        self.logger.info('Fechando driver')
        self.context.close()
        self.browser.close()
        self.playwright.stop()
    
    @property
    def driver(self) -> Page:
        return self.page

    