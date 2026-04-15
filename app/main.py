from fastapi import FastAPI
from pydantic import BaseModel

from servico_intencao import identificar_intencao
from servico_clima import obter_clima
from servico_comex import obter_dados_comex
from servico_ia import gerar_resposta_ia


app = FastAPI()


# 📦 Modelo de entrada da mensagem
class MensagemEntrada(BaseModel):
    texto: str


# 🔎 Rota de teste
@app.get("/health")
def health_check():
    return {"status": "ok"}


# 💬 Rota principal do chatbot
@app.post("/mensagem")
def processar_mensagem(mensagem: MensagemEntrada):
    texto_usuario = mensagem.texto

    # 1. Identificar intenção
    intencao = identificar_intencao(texto_usuario)

    # 2. Executar fluxo baseado na intenção
    if intencao == "clima":
        dados = obter_clima(texto_usuario)
        resposta = gerar_resposta_ia(texto_usuario, dados)

    elif intencao == "comex":
        dados = obter_dados_comex(texto_usuario)
        resposta = gerar_resposta_ia(texto_usuario, dados)

    elif intencao == "resumo":
        dados_clima = obter_clima(texto_usuario)
        dados_comex = obter_dados_comex(texto_usuario)

        dados = {
            "clima": dados_clima,
            "comex": dados_comex
        }

        resposta = gerar_resposta_ia(texto_usuario, dados)

    else:
        resposta = "Desculpe, não consegui entender sua solicitação."

    return {"resposta": resposta}