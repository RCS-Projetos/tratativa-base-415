# RPA Base SSW 🚀

Este projeto é um pacote Python base (`ssw`) para a criação de robôs (RPA) que interagem com o sistema **SSW** utilizando Selenium. Ele serve como infraestrutura central, lidando com configurações de navegador, login e navegação básica, permitindo que outros projetos foquem apenas na extração e tratativa dos relatórios específicos.

## 📦 Instalação

O projeto foi estruturado para ser utilizado como um pacote Python (Installable Package). Você pode instalá-lo diretamente do GitHub no seu projeto principal utilizando o `pip` ou `uv`.

```bash
# Instalação direto do repositório (via pip)
pip install git+https://github.com/RCS-Projetos/RPA-BASE-SSW.git

# Instalação direto do repositório (via uv)
uv pip install git+https://github.com/RCS-Projetos/RPA-BASE-SSW.git
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.13+**
- **Selenium** (para automação web)
- **webdriver-manager** (gerenciamento automático de drivers)
- **pandas** e **numpy** (para manipulação de dados em extensões)
- **python-dotenv** (gerenciamento de variáveis de ambiente)
- **hatchling** (backend para empacotamento)

## ⚙️ Variáveis de Ambiente necessárias

Crie um arquivo `.env` na raiz do projeto que for utilizar esta base e preencha as credenciais. O pacote buscará essas chaves automaticamente:

```env
SSW_COMPANY=sua_empresa
SSW_TAX=seu_cnpj_ou_filial
SSW_USER=seu_usuario
SSW_PASSWORD=sua_senha
```

## 🚀 Como usar nos seus scripts

Ao instalar o pacote no seu projeto, você poderá importar as classes base para criar o seu próprio robô do zero, ou instanciar para navegar nos relatórios do sistema SSW.

### Exemplo Básico de Inicialização

```python
from ssw import SSW
from ssw.selenium import Driver

# 1. Inicia o driver do Selenium (headless=True para rodar em background)
driver = Driver(headless=False, download_dir='Downloads')

# 2. Instancia a base principal do SSW
ssw_bot = SSW(driver=driver)

# 3. Faz o login utilizando as credenciais do .env
ssw_bot.make_login()

# ... Lógica customizada ...

# 4. Finaliza e fecha o navegador
ssw_bot.close()
```

### Exemplo Acessando e Preenchendo um Relatório

Se quiser reaproveitar as ferramentas de relatório, utilize a classe `ReportSSW`:

```python
from ssw import SSW
from ssw.selenium import Driver
from ssw.report import ReportSSW

driver = Driver(headless=False)
ssw_bot = SSW(driver=driver)

# Realiza o Login
ssw_bot.make_login()

# Prepara a extração de relatórios
relatorio = ReportSSW(driver=driver)

# Método utilitário de preenchimento (depende da sua sobrescrita/uso)
relatorio.use_initial_parameters(branch="SPO", report="209")

# Por fim, encerra:
ssw_bot.close()
```

## 🏗️ Estrutura do Pacote

- `ssw/`: Pasta raiz do pacote embutido.
  - `ssw.py`: Classe principal (`SSW`) que orquestra setup e login.
  - `report.py`: Classe modelo `ReportSSW` para lidar com relatórios específicos.
  - `selenium/driver.py`: Encapsulamento customizado do `webdriver.Chrome` (gestão limpa de janelas e downloads).
  - `functions/login.py`: Automatização completa dos passos no formulário de acesso ao sistema.
  - `functions/logger.py`: Ferramenta para gerenciar de forma amigável os logs no console.

## 👥 Contribuições

Este repositório é projetado para atuar como _CORE_ dos robôs da empresa. Qualquer alteração inserida aqui será refletida em todos os projetos que consomem o pacote. Teste bem antes de abrir os commits!
# tratativa-base-415
# tratativa-base-415
