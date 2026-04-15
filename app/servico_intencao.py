import unicodedata


def normalizar_texto(texto: str) -> str:
    """
    Remove acentos e coloca em minúsculo
    """
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto


def identificar_intencao(texto: str) -> str:
    """
    Identifica a intenção do usuário com base em palavras-chave
    Retorna: clima | comex | resumo | desconhecido
    """

    texto = normalizar_texto(texto)

    # 🔹 Palavras-chave clima
    palavras_clima = [
        "clima", "tempo", "chuva", "temperatura", "previsao",
        "vai chover", "sol", "nublado"
    ]

    # 🔹 Palavras-chave Comex (exportação / agro)
    palavras_comex = [
        "exportacao", "exportacoes", "produto", "comex",
        "exportado", "agro", "soja", "milho", "boi"
    ]

    # 🔹 Palavras-chave resumo (mais amplas)
    palavras_resumo = [
        "resumo", "analise", "cenario", "situacao",
        "geral", "como esta hoje", "panorama"
    ]

    # 🔍 Verificações

    # Prioridade: resumo (pois pode envolver múltiplos serviços)
    if any(p in texto for p in palavras_resumo):
        return "resumo"

    if any(p in texto for p in palavras_clima):
        return "clima"

    if any(p in texto for p in palavras_comex):
        return "comex"

    return "desconhecido"