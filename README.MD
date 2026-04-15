cat > README.md << 'EOF'
# 🌾 Agro Chatbot Inteligente

Chatbot de inteligência artificial voltado ao setor agropecuário, capaz de consultar dados de clima e comércio exterior (Comex Stat) e responder perguntas de forma simples via Telegram.

---

## 🚀 Visão Geral

O projeto consiste em um chatbot integrado ao Telegram que permite ao usuário:

- 🌦️ Consultar o clima de uma cidade
- 📊 Obter informações sobre exportações do agronegócio brasileiro
- 🧠 Receber um resumo inteligente combinando clima e mercado

O objetivo é fornecer informações úteis de forma rápida, acessível e em linguagem natural.

---

## 🧠 Funcionalidades

### 1. Consulta de clima
- Busca condições atuais do tempo por cidade
- Dados como temperatura, umidade e condição climática

Exemplo:
clima em Goiânia

---

### 2. Consulta de exportações (Comex Stat)
- Identifica o principal produto exportado em determinado período
- Utiliza dados oficiais do governo brasileiro

Exemplo:
exportações 2025

---

### 3. Resumo inteligente
- Combina dados de clima e mercado
- Gera uma resposta interpretativa

Exemplo:
resumo do cenário hoje

---

## 🏗️ Arquitetura

Telegram → Bot → API (FastAPI) → Serviços → APIs externas → Resposta

---

## 📁 Estrutura do Projeto

agro-chatbot/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ bot_telegram.py
│  ├─ configuracao.py
│  ├─ servico_intencao.py
│  ├─ servico_clima.py
│  ├─ servico_comex.py
│  └─ servico_ia.py
├─ .env
├─ requirements.txt
└─ README.md

---

## ⚙️ Tecnologias Utilizadas

- Python
- FastAPI
- Requests
- Telegram Bot API
- Open-Meteo API
- Comex Stat API

---

## 🔧 Como Executar

### 1. Clone o repositório

git clone https://github.com/SEU_USUARIO/agro-chatbot.git
cd agro-chatbot

---

### 2. Instale as dependências

py -m pip install fastapi uvicorn requests python-dotenv

---

### 3. Configure o .env

TELEGRAM_TOKEN=SEU_TOKEN_AQUI
URL_API=http://localhost:8000

---

### 4. Inicie a API

py -m uvicorn app.main:app --reload

---

### 5. Inicie o bot

py -m app.bot_telegram

---

### 6. Teste no Telegram

clima em Goiânia  
exportações 2025  
resumo do cenário hoje  

---

## 🔐 Segurança

- O arquivo .env não deve ser versionado
- Tokens e credenciais são mantidos fora do código

---

## 📊 Uso de IA

Neste projeto, a camada de IA é implementada por meio de regras de geração de resposta baseadas nos dados retornados pelas APIs.

Possíveis evoluções incluem:
- Integração com LLMs (OpenAI, Ollama)
- Classificação de intenção com IA
- Respostas mais contextuais

---

## 🚧 Melhorias Futuras

- Melhorar extração de cidade
- Refinar parsing dos dados do Comex Stat
- Adicionar suporte a múltiplos produtos
- Implementar IA real com LLM
- Criar interface web

---

## 👨‍💻 Autor

Desenvolvido como parte de desafio técnico para vaga de desenvolvedor.

---

## 📌 Considerações Finais

Este projeto demonstra:

- Integração com APIs externas
- Estruturação de backend com FastAPI
- Construção de chatbot funcional
- Capacidade de organizar e entregar um produto completo

EOF