import pytest
from app.servico_intencao import identificar_intencao


def test_intencao_clima():
    texto = "Como está o clima em Goiânia?"
    resultado = identificar_intencao(texto)
    assert resultado == "clima"


def test_intencao_comex():
    texto = "Qual foi o produto mais exportado em 2025?"
    resultado = identificar_intencao(texto)
    assert resultado == "comex"


def test_intencao_resumo():
    texto = "Me dê um resumo do cenário atual"
    resultado = identificar_intencao(texto)
    assert resultado == "resumo"


def test_intencao_fora_escopo():
    texto = "Qual o preço da soja?"
    resultado = identificar_intencao(texto)
    assert resultado == "fora_escopo"


def test_intencao_desconhecida():
    texto = "asdfghjkl"
    resultado = identificar_intencao(texto)
    assert resultado in ["desconhecido", "fora_escopo"]