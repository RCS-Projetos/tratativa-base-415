import logging
from src.websocket.driver import Driver


class Login:
    def __init__(
        self,
        driver: Driver,
        company: str,
        tax: str,
        user: str,
        password: str,
        url: str = 'https://sistema.ssw.inf.br/bin/ssw0422',
        campany_xpath: str = 'xpath=/html/body/form/input[1]',
        tax_xpath: str = 'xpath=/html/body/form/input[2]',
        user_xpath: str = 'xpath=/html/body/form/input[3]',
        password_xpath: str = 'xpath=/html/body/form/input[4]',
        send_xpath: str = 'xpath=/html/body/form/a'
    ):
        self.logger = logging.getLogger('login')
        self.page = driver.page # Acessamos a página do Playwright
        self.company = company
        self.tax = tax
        self.user = user
        self.password = password
        self.url = url
        self.campany_xpath = campany_xpath
        self.tax_xpath = tax_xpath
        self.user_xpath = user_xpath
        self.password_xpath = password_xpath
        self.send_xpath = send_xpath 
        
    def login(self):
        self.logger.info('Iniciando processo de login')
        self.page.goto(self.url)
        
        inputs = [
            (self.campany_xpath, self.company),
            (self.tax_xpath, self.tax),
            (self.user_xpath, self.user),
            (self.password_xpath, self.password)
        ]
        
        for xpath, value in inputs:
            # O Playwright espera o elemento aparecer automaticamente
            # Usamos o evaluate para manter sua lógica de injeção via JS (arguments[0].value)
            element = self.page.locator(xpath)
            element.evaluate("(el, val) => el.value = val", value)
        
        # Clique no botão de enviar
        self.page.locator(self.send_xpath).click()
        
        self.logger.info("Login submetido")
        
        self.check_login()
        
    
    def check_login(self):
        self.logger.info('Verificando login')
        self.page.wait_for_url('https://sistema.ssw.inf.br/bin/menu01')
        self.logger.info('Login efetuado com sucesso')