from fastapi import FastAPI
from pydantic import BaseModel

from app.servico_intencao import identificar_intencao
from app.servico_clima import obter_clima
from app.servico_comex import obter_dados_comex
from app.servico_ia import gerar_resposta_ia


app = FastAPI()


# 📦 Modelo de entrada
class MensagemEntrada(BaseModel):
    texto: str


# 🔎 Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}


# 💬 Rota principal
@app.post("/mensagem")
def processar_mensagem(mensagem: MensagemEntrada):
    texto_usuario = mensagem.texto.strip()

    if not texto_usuario:
        return {"resposta": "Por favor, envie uma mensagem válida."}

    try:
        # 1. Identificar intenção
        intencao = identificar_intencao(texto_usuario)

        # 2. Fluxo por intenção
        if intencao == "clima":
            dados = obter_clima(texto_usuario)

        elif intencao == "comex":
            dados = obter_dados_comex(texto_usuario)

        elif intencao == "resumo":
            dados_clima = obter_clima(texto_usuario)
            dados_comex = obter_dados_comex(texto_usuario)

            dados = {
                "clima": dados_clima,
                "comex": dados_comex
            }
        elif intencao == "fora_escopo":
            return {
                "resposta": "Posso te ajudar com clima, exportações ou resumo do cenário."
            }

        else:
            return {"resposta": "Desculpe, não entendi sua solicitação."}

        # 3. Gerar resposta final
        resposta = gerar_resposta_ia(texto_usuario, dados)

        return {"resposta": resposta}

    except Exception as e:
        print(f"Erro no processamento: {e}")
        return {"resposta": "Ocorreu um erro ao processar sua solicitação."}