from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
from report import new_report
import uvicorn

app = FastAPI(title="SSW - Comission Client")


@app.get("/api/v1/comission/{id}")
def get_seler_comission(id: str):
    try:
        data = new_report.execute_report(url="https://sistema.ssw.inf.br/bin/ssw0014", vendedor_id=id)

        df = pd.DataFrame(data)
        
        try:
            print('Corrigindo Percentuais')
            cols_pct = ['Conquista_Pct', 'Manut_1_Pct', 'Manut_2_Pct']
            for col in cols_pct:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")
        
        try:
            print('Corrigindo Datas e Formatos de Ano')
            cols_data = [
                'Conquista_Inicio', 'Conquista_Fim', 
                'Manut_1_Inicio', 'Manut_1_Fim', 
                'Manut_2_Inicio', 'Manut_2_Fim'
            ]

            def normalizar_ano_ssw(data_str):
                if pd.isna(data_str) or str(data_str).strip() == "":
                    return None
                
                partes = str(data_str).split('/')
                if len(partes) == 3:
                    dia, mes, ano = partes
                    # Se o ano tiver apenas 2 dígitos, aplica a regra do SSW
                    if len(ano) == 2:
                        ano_int = int(ano)
                        # Regra SSW: >= 70 vira 19xx, < 70 vira 20xx
                        ano = str(1900 + ano_int) if ano_int >= 70 else str(2000 + ano_int)
                        return f"{dia}/{mes}/{ano}"
                return data_str

            for col in cols_data:
                # 1. Aplica a correção de 2 para 4 dígitos antes da conversão
                df[col] = df[col].apply(normalizar_ano_ssw)
                
                # 2. Converte para Datetime (Trata NaT para anos > 2262 como 2999)
                # O Pandas não suporta o ano 2999 como objeto de tempo
                # Por isso, convertemos e formatamos de volta para string imediatamente
                df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

            # --- TRATAMENTO FINAL PARA JSON ---
            # Garante que NaT ou NaN não quebrem o FastAPI
            df = df.replace({np.nan: None, "NaT": None, "nan": None})

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro na normalização de datas: {str(e)}")

        try:
            print('Corrigindo valores nulos')
            df = df.where(pd.notnull(df), None)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

        return {
            "status": "success",
            "seler_code": id,
            "total_registers": len(df),
            "data": df.to_dict(orient="records")
        }


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)