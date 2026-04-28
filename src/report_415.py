from .websocket.driver import Driver
from .functions.fetch_consult import FetchConsult

class Report415(FetchConsult):
    def __init__(self, driver: Driver):
        super().__init__(driver)
        
    def script(self) -> str:
        return """
    async ([url, vendedor_id]) => {
        const formData = new URLSearchParams();
        formData.append('act', 'VEN');
        formData.append('t_con_vend', vendedor_id);
        formData.append('dummy', new Date().getTime());

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });

            const buffer = await response.arrayBuffer();
            const decoder = new TextDecoder('iso-8859-1'); 
            const htmlString = decoder.decode(buffer);
            
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlString, "text/html");
            const xmlContainer = doc.getElementById('xmlsr');

            if (!xmlContainer) {
                return { error: "Container xmlsr não encontrado" };
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
                        valorDecimal = numero / 100;
                    }
                }
                
                const datasEncontradas = (textoLimpo.match(/\\d{2}\\/\\d{2}\\/\\d{2,4}/g) || []).map(dt => {
                    return dt.endsWith('/99') ? dt.replace('/99', '/2099') : dt;
                });

                return [valorDecimal, datasEncontradas[0] || "", datasEncontradas[1] || ""];
            };

            return registros.map(reg => {
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
        } catch (err) {
            return { error: err.message };
        }
    }
    """
    
    def run(self, vendedor_id: str):
        return self.fetch_consult(vendedor_id=vendedor_id)
        
        