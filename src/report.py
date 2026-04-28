
import logging
import uuid
import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from .websocket.driver import Driver
from .functions.login import Login
from .functions.url_access import UrlAccess
from .report_415 import Report415
from models import db, Vendedor, Comissao

class Report:
    def __init__(self, user: dict, url: str, headless: bool = True):
        self.driver = Driver(headless=headless)
        self.login = Login(
            driver=self.driver,
            **user
        )
        self.url = UrlAccess(
            driver=self.driver,
            url=url
        )
        self.report_415 = Report415(
            driver=self.driver
        )
        self.page = self.driver.page
        self.logger = logging.getLogger('report')

    def run(self, session_id: str, codes: list[str] = []):
        try:
            self.logger.info('Iniciando busca de dados relatório 415')
            self.login.login()
            self.url.url_access()
            
            self.logger.info('Buscando vendedores no banco de dados')
            if not codes:
                sellers = Vendedor.query.filter_by(session_id=session_id).all()
                codes = [seller.codigo for seller in sellers]
            

            for code in codes:
                self.logger.info(f'Buscando dados do vendedor {code}')
                seller = Vendedor.query.filter_by(session_id=session_id, codigo=code).first()
                if not seller: continue
                
                try:
                    seller.status = 'Processando...'
                    db.session.commit()
                    
                    
                    data = self.report_415.run(code)
                    time.sleep(random.randint(5, 10))
                    
                    if not data or len(data) == 0:
                        seller.status = 'Vazio'
                    else:
                        consult_id = str(uuid.uuid4())[:8]
                        
                        def safe_float(val):
                            if val is None or val == '':
                                return None
                            try:
                                return float(val)
                            except ValueError:
                                return None
                        
                        seller.status = 'Sucesso'
                        
                        for row in data:
                            comission = Comissao(
                                session_id=session_id,
                                consulta_id=consult_id,
                                vendedor_id=seller.id,
                                equipe=seller.equipe,
                                codigo=seller.codigo,
                                vendedor=seller.vendedor_nome,
                                filial=seller.filial,
                                nome_vendedor=seller.nome_completo,
                                clientes=row.get('Clientes', ''),
                                cnpj=row.get('CNPJ', ''),
                                cidade=row.get('Cidade', ''),
                                nome_cliente=row.get('Nome', ''),
                                conquista_inicio=row.get('Conquista_Inicio', ''),
                                conquista_fim=row.get('Conquista_Fim', ''),
                                conquista_pct=safe_float(row.get('Conquista_Pct')),
                                manut_1_inicio=row.get('Manut_1_Inicio', ''),
                                manut_1_fim=row.get('Manut_1_Fim', ''),
                                manut_1_pct=safe_float(row.get('Manut_1_Pct')),
                                manut_2_inicio=row.get('Manut_2_Inicio', ''),
                                manut_2_fim=row.get('Manut_2_Fim', ''),
                                manut_2_pct=safe_float(row.get('Manut_2_Pct')),
                                mercadoria=row.get('Mercadoria', ''),
                                observacao=row.get('Observacao', '')
                            )
                            db.session.add(comission)
                        
                        consultas_unicas = db.session.query(Comissao.consulta_id).filter_by(session_id=session_id, vendedor_id=seller.id).distinct().all()
                        if len(consultas_unicas) > 3:
                            oldest_id = consultas_unicas[0][0]
                            Comissao.query.filter_by(session_id=session_id, vendedor_id=seller.id, consulta_id=oldest_id).delete()
                    
                    seller.ultima_consulta = datetime.now(ZoneInfo('America/Sao_Paulo')).replace(tzinfo=None)
                    db.session.commit()
                    yield {"codigo": code, "status": seller.status}
                    self.logger.info(f'Dados do vendedor {code} buscados com sucesso')
                    seller.status = 'Sucesso'
                    db.session.commit()
                
                except Exception as e:
                    seller.status = 'Erro'
                    db.session.commit()
                    yield {"codigo": code, "status": "Erro", "msg": str(e)}
                    self.logger.error(f'Erro ao buscar dados do vendedor {code}: {str(e)}')

            self.driver.page.wait_for_timeout(5000)
        except Exception as e:
            self.logger.error(f'Erro ao executar: {str(e)}')
        
        finally:
            self.logger.info('Encerrando busca de dados relatório 415')
            self.driver.quit()
            self.logger.info('Driver encerrado com sucesso')
