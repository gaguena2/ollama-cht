# ollama-cht

Backend que integra o [Ollama](https://github.com/ollama/ollama) (LLM local, via REST API) com um canal de mensagens — hoje com um endpoint stub, pensado para futuramente receber mensagens do WhatsApp e responder usando o modelo rodando no Ollama.

## Arquitetura

O backend (`ollama_cht/`) segue **DDD (Domain-Driven Design)**, separado em camadas:

```
ollama_cht/
├── domain/           # regras de negócio puras, sem dependência de framework
│   ├── entities.py       # Conversation, Message
│   └── repositories.py   # ConversationRepository (interface)
├── application/      # orquestra o caso de uso
│   ├── ports.py           # ChatModelPort (interface)
│   └── use_cases.py       # SendMessageUseCase
├── infrastructure/   # implementações concretas (adapters)
│   ├── ollama_client.py          # ChatModelPort via REST (httpx)
│   └── persistence/              # ConversationRepository via Postgres (SQLAlchemy)
├── interfaces/api/   # camada HTTP (FastAPI)
│   └── routers/
│       ├── health.py
│       └── webhook.py    # POST /webhook/whatsapp (stub de entrada de mensagens)
├── config.py          # configuração via variáveis de ambiente
├── dependencies.py    # injeção de dependência (liga as camadas)
└── main.py            # cria a app FastAPI
```

A ideia da separação: `domain` e `application` não sabem que existe Postgres, FastAPI ou Ollama — só conhecem interfaces (`ConversationRepository`, `ChatModelPort`). Quem implementa essas interfaces fica em `infrastructure`. Isso permite trocar, por exemplo, Postgres por outro banco, ou o cliente HTTP do Ollama por outro modelo, sem tocar nas regras de negócio.

### Fluxo de uma mensagem

1. `POST /webhook/whatsapp` recebe `{"from": "<id>", "message": "<texto>"}` (hoje é um stub — ainda não há integração real com a API do WhatsApp).
2. `SendMessageUseCase` carrega o histórico da conversa no Postgres (se existir), adiciona a mensagem do usuário.
3. Chama o Ollama (`POST /api/chat`) enviando o histórico completo (a API do Ollama é stateless).
4. Salva a resposta do modelo no histórico e retorna.

## Stack

- **FastAPI** + **Uvicorn** — API assíncrona.
- **httpx** — cliente HTTP para o Ollama.
- **SQLAlchemy (async) + asyncpg** — persistência do histórico de conversas no Postgres.
- **pydantic-settings** — configuração via `.env`.

## Como rodar

```bash
cp .env.example .env   # ajuste as credenciais do Postgres se quiser
docker compose up -d --build
```

Isso sobe três containers:

| Serviço  | O que é                                  | Exposto no host? |
|----------|-------------------------------------------|-------------------|
| `ollama` | motor do LLM (REST API)                   | não (só rede interna) |
| `db`     | Postgres (histórico das conversas)        | não (só rede interna) |
| `app`    | este backend (FastAPI)                    | sim, porta `8000` |

Depois de subir, baixe o modelo pelo menos uma vez (fica persistido no volume `ollama_data`, não precisa repetir em todo restart):

```bash
docker exec -it ollama ollama pull qwen3:0.6b
```

Teste o endpoint:

```bash
curl -X POST localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"from": "5511999999999", "message": "Olá, tudo bem?"}'
```

Comandos de teste direto no Ollama (sem passar pelo backend) estão em [`commands`](./commands).

## Variáveis de ambiente (`.env`)

| Variável           | Descrição                                          | Default (compose) |
|--------------------|-----------------------------------------------------|--------------------|
| `OLLAMA_BASE_URL`  | URL do Ollama                                       | `http://ollama:11434` |
| `OLLAMA_MODEL`     | modelo usado nas conversas                          | `qwen3:0.6b` |
| `DATABASE_URL`     | string de conexão do Postgres (driver async)        | `postgresql+asyncpg://...@db:5432/...` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | credenciais do Postgres | `ollama_cht` |

## Limitações atuais / próximos passos

- `/webhook/whatsapp` é um **stub**: recebe uma mensagem e devolve a resposta no corpo do HTTP, mas não fala com a API oficial do WhatsApp ainda. Quando essa integração for feita (ex: WhatsApp Cloud API), esse endpoint deve ser adaptado para o formato do webhook da Meta e um adapter de saída precisa enviar a resposta de volta via Graph API.
- Não há reverse proxy / HTTPS configurado — para expor a VPS publicamente, é necessário colocar algo como nginx ou Caddy na frente do serviço `app`.
- Tabelas do Postgres são criadas automaticamente no startup (`Base.metadata.create_all`); não há ferramenta de migração (ex: Alembic) ainda — se o schema mudar, isso precisará ser revisto.
