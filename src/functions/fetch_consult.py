import logging
from ..websocket.driver import Driver


class FetchConsult:
    def __init__(self, driver: Driver):
        self.driver = driver
        self.logger = logging.getLogger('fetch_consult')
    
    def fetch_consult(self, **kwargs):
        self.logger.info(f"Iniciando extração via Fetch")
        url = self.driver.page.url
        script = self.script()

        self.logger.info(f"Enviando requisição para a URL: \t{url}")
        self.logger.info(f"Com os parâmetros: \t{kwargs}")
        
        try:
            self.logger.info("Aguardando resposta...")
            payload = self.driver.page.evaluate(script, [url, *kwargs.values()])
            self.logger.info("Resposta recebida com sucesso")
            
            if isinstance(payload, dict) and 'error' in payload:
                raise Exception(payload['error'])
            
            self.logger.info("Dados processados com sucesso")
            return payload

        except Exception as e:
            self.logger.error(f"Erro ao executar fetch: {str(e)}")
            raise e
        
        
    def script(self) -> str:
        return """
        
        """
        
        
        
        
