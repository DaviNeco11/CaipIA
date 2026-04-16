import requests
from app.configuracao import OLLAMA_URL, OLLAMA_MODELO


CATEGORIAS_VALIDAS = {"clima", "comex", "resumo", "fora_escopo"}


def identificar_intencao(texto: str) -> str:
    prompt = f"""
Você é um classificador de intenções para um chatbot do agronegócio.

Classifique a mensagem do usuário em apenas UMA destas categorias:
- clima
- comex
- resumo
- fora_escopo

Regras:
- "clima": perguntas sobre tempo, chuva, temperatura, previsão do tempo, clima de uma cidade.
- "comex": perguntas sobre exportações, importações, produto exportado, valor exportado, comércio exterior, Comex Stat.
- "resumo": pedidos de panorama, resumo, análise geral, cenário atual.
- "fora_escopo": preço, cotação, valor de mercado, quanto custa, opiniões, assuntos que não sejam clima/comex/resumo.

Importante:
- Perguntas sobre PREÇO ou COTAÇÃO são sempre "fora_escopo".
- Perguntas sobre PRODUTO MAIS EXPORTADO ou EXPORTAÇÕES são sempre "comex".
- Responda somente com uma palavra exata da lista.
- Não explique.
- Não use pontuação.
- Não escreva mais nada.

Mensagem do usuário:
{texto}
""".strip()

    url = f"{OLLAMA_URL}/api/chat"

    payload = {
        "model": OLLAMA_MODELO,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    try:
                # 🔎 DEBUG - entrada enviada ao Ollama
        print("\n=== OLLAMA INPUT ===")
        print(prompt)

        resposta = requests.post(url, json=payload, timeout=30)
        resposta.raise_for_status()

        dados_resposta = resposta.json()

        texto_resposta = (
            dados_resposta
            .get("message", {})
            .get("content", "")
            .strip()
            .lower()
        )

        # 🔎 DEBUG - saída do Ollama
        print("\n=== OLLAMA OUTPUT ===")
        print(texto_resposta)
        print("====================\n")

        # normalização defensiva
        texto_resposta = texto_resposta.replace(".", "").replace(",", "").strip()

        if texto_resposta in CATEGORIAS_VALIDAS:
            return texto_resposta

        # fallback simples
        texto_lower = texto.lower()
        if any(p in texto_lower for p in ["preço", "preco", "cotação", "cotacao", "quanto custa"]):
            return "fora_escopo"
        if any(p in texto_lower for p in ["exportação", "exportacoes", "exportações", "exportado", "comex"]):
            return "comex"
        if any(p in texto_lower for p in ["clima", "tempo", "chuva", "temperatura"]):
            return "clima"
        if any(p in texto_lower for p in ["resumo", "cenário", "cenario", "panorama", "análise", "analise"]):
            return "resumo"

        return "desconhecido"

    except Exception as e:
        print(f"Erro na classificação: {e}")
        return "desconhecido"