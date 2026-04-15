import requests
import re


def extrair_cidade(texto: str) -> str | None:
    """
    Tenta extrair a cidade a partir de padrões simples.
    Exemplos:
    - "Como está o clima em Goiânia?"
    - "Vai chover em Rio Verde amanhã?"
    """
    padroes = [
        r"em\s+([A-Za-zÀ-ÖØ-öø-ÿ\s\-]+)",
        r"para\s+([A-Za-zÀ-ÖØ-öø-ÿ\s\-]+)"
    ]

    for padrao in padroes:
        resultado = re.search(padrao, texto, re.IGNORECASE)
        if resultado:
            cidade = resultado.group(1).strip(" ?.!,;:")
            return cidade

    return None


def buscar_coordenadas(cidade: str) -> dict | None:
    """
    Consulta a API de geocoding da Open-Meteo para obter latitude e longitude.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": cidade,
        "count": 1,
        "language": "pt",
        "format": "json"
    }

    try:
        resposta = requests.get(url, params=params, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()

        resultados = dados.get("results")
        if not resultados:
            return None

        local = resultados[0]
        return {
            "cidade": local.get("name"),
            "latitude": local.get("latitude"),
            "longitude": local.get("longitude"),
            "pais": local.get("country"),
            "estado": local.get("admin1")
        }

    except requests.RequestException:
        return None


def buscar_clima(latitude: float, longitude: float) -> dict | None:
    """
    Consulta a API de forecast da Open-Meteo para obter dados atuais.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
        "timezone": "America/Sao_Paulo"
    }

    try:
        resposta = requests.get(url, params=params, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()

        atual = dados.get("current")
        if not atual:
            return None

        return {
            "temperatura": atual.get("temperature_2m"),
            "umidade": atual.get("relative_humidity_2m"),
            "sensacao_termica": atual.get("apparent_temperature"),
            "precipitacao": atual.get("precipitation"),
            "codigo_tempo": atual.get("weather_code"),
            "vento": atual.get("wind_speed_10m"),
            "horario": atual.get("time")
        }

    except requests.RequestException:
        return None


def traduzir_codigo_tempo(codigo: int | None) -> str:
    """
    Traduz alguns códigos de tempo da Open-Meteo para descrição em português.
    """
    mapa = {
        0: "céu limpo",
        1: "predominantemente limpo",
        2: "parcialmente nublado",
        3: "encoberto",
        45: "neblina",
        48: "neblina com geada",
        51: "garoa leve",
        53: "garoa moderada",
        55: "garoa intensa",
        61: "chuva fraca",
        63: "chuva moderada",
        65: "chuva forte",
        71: "neve fraca",
        73: "neve moderada",
        75: "neve forte",
        80: "pancadas de chuva fracas",
        81: "pancadas de chuva moderadas",
        82: "pancadas de chuva fortes",
        95: "trovoada",
        96: "trovoada com granizo fraco",
        99: "trovoada com granizo forte"
    }
    return mapa.get(codigo, "condição climática não identificada")


def obter_clima(texto_usuario: str) -> dict:
    """
    Função principal do serviço de clima.
    Recebe o texto do usuário, extrai a cidade, busca coordenadas e consulta o clima.
    """
    cidade = extrair_cidade(texto_usuario)

    if not cidade:
        return {
            "sucesso": False,
            "mensagem": "Não consegui identificar a cidade informada."
        }

    localizacao = buscar_coordenadas(cidade)
    if not localizacao:
        return {
            "sucesso": False,
            "mensagem": f"Não consegui localizar a cidade '{cidade}'."
        }

    clima = buscar_clima(localizacao["latitude"], localizacao["longitude"])
    if not clima:
        return {
            "sucesso": False,
            "mensagem": "Não foi possível consultar o clima no momento."
        }

    return {
        "sucesso": True,
        "tipo": "clima",
        "cidade": localizacao["cidade"],
        "estado": localizacao["estado"],
        "pais": localizacao["pais"],
        "temperatura": clima["temperatura"],
        "umidade": clima["umidade"],
        "sensacao_termica": clima["sensacao_termica"],
        "precipitacao": clima["precipitacao"],
        "vento": clima["vento"],
        "descricao": traduzir_codigo_tempo(clima["codigo_tempo"]),
        "horario_consulta": clima["horario"]
    }