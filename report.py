from ssw import SSW
from ssw.selenium import Driver


class Report(SSW):
    def __init__(self, driver: Driver, company: str, tax: str, user: str, password: str, download_dir: str = 'Downloads'):
        super().__init__(driver, company, tax, user, password, download_dir)

    

    def report(self, url: str, vendedor_id: int):
        script = """
        const callback = arguments[arguments.length - 1]; // Callback obrigatório do Selenium Async
        const url = arguments[0];
        const vendedor_id = arguments[1];

        // Monta o FormData conforme as imagens do seu console
        const formData = new URLSearchParams();
        formData.append('act', 'VEN');
        formData.append('t_con_vend', vendedor_id);
        formData.append('dummy', new Date().getTime());

        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.arrayBuffer())
        .then(buffer => {
            const decoder = new TextDecoder('iso-8859-1'); // Respeita a codificação do SSW
            const htmlString = decoder.decode(buffer);
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlString, "text/html");
            const xmlContainer = doc.getElementById('xmlsr');

            if (!xmlContainer) {
                callback({error: "Container xmlsr não encontrado"});
                return;
            }

            const registros = Array.from(xmlContainer.querySelectorAll('r'));

            const extrairDadosComissao = (textoRaw) => {
                if (!textoRaw || textoRaw.trim() === "") return ["", "", ""];
                const textoLimpo = textoRaw.replace(/\\u00A0/g, ' ').replace(/\\s+/g, ' ').trim();
                
                const pctMatch = textoLimpo.match(/([\\d.,]+)%/);
                let valorDecimal = "";
                if (pctMatch) {
                    let numero = parseFloat(pctMatch[1].replace(',', '.'));
                    if (!isNaN(numero)) {
                        valorDecimal = numero / 100; // Retorna como número real para o Pandas
                    }
                }
                
                const datasEncontradas = (textoLimpo.match(/\\d{2}\\/\\d{2}\\/\\d{2,4}/g) || []).map(dt => {
                    return dt.endsWith('/99') ? dt.replace('/99', '/2099') : dt;
                });

                return [valorDecimal, datasEncontradas[0] || "", datasEncontradas[1] || ""];
            };

            const dataRows = registros.map(reg => {
                const getVal = (tag) => reg.querySelector(tag)?.textContent.trim() || "";
                const [p1, i1, f1] = extrairDadosComissao(getVal('f5'));
                const [p2, i2, f2] = extrairDadosComissao(getVal('f6'));
                const [p3, i3, f3] = extrairDadosComissao(getVal('f7'));

                return {
                    "CNPJ": getVal('f0'),
                    "Nome": getVal('f1'),
                    "Filial": getVal('f2'),
                    "Cidade": getVal('f3'),
                    "Mercadoria": getVal('f4'),
                    "Conquista_Pct": p1,
                    "Conquista_Inicio": i1,
                    "Conquista_Fim": f1,
                    "Manut_1_Pct": p2,
                    "Manut_1_Inicio": i2,
                    "Manut_1_Fim": f2,
                    "Manut_2_Pct": p3,
                    "Manut_2_Inicio": i3,
                    "Manut_2_Fim": f3
                };
            });

            callback(dataRows); // Retorna a lista de objetos para o Python
        })
        .catch(err => callback({error: err.message}));
        """

        self.logger.info("Iniciando extração via Fetch")

        
        payload = self.driver().driver().execute_async_script(script, url, vendedor_id)
        if isinstance(payload, dict) and 'error' in payload:
            raise Exception(payload['error'])
        else:
            return payload