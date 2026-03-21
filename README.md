# Excel API

API **FastAPI** que recebe um JSON com metadados e linhas de atividade, preenche um modelo Excel (`.xlsx`) e devolve o ficheiro gerado.

## Requisitos

- Python **3.11** ou superior
- [uv](https://docs.astral.sh/uv/) (gestor de dependências e ambiente)
- Ficheiros obrigatórios na pasta `templates/` (ver [Configuração](#configuração))

## Instalação

Na raiz do repositório:

```bash
uv sync
```

Com dependências de desenvolvimento (testes, cobertura, etc.):

```bash
uv sync --group dev
```

Equivalente: `make install` (executa `uv sync`).

## Como iniciar o projeto

### Modo desenvolvimento (recomendado)

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Ou:

```bash
make up
```

### Alternativa

```bash
uv run python -m src.main
```

O serviço fica em **http://localhost:8000**.

- **Saúde**: `GET http://localhost:8000/health`
- **OpenAPI (JSON)**: `GET http://localhost:8000/docs` devolve o schema OpenAPI (não é a UI Swagger interativa; use uma ferramenta como Postman ou `curl` conforme abaixo)

## Endpoint principal: gerar Excel

| Método | URL               | Corpo        | Resposta (sucesso)      |
|--------|-------------------|-------------|-------------------------|
| `POST` | `/generate-excel` | JSON        | Ficheiro `.xlsx` (binário) |

**Cabeçalho obrigatório:** `Content-Type: application/json`

### Formato do JSON (corpo do POST)

O corpo deve ser um objeto JSON com:

- **`meta`** (objeto, obrigatório): campos opcionais para o cabeçalho do relatório  
  - `empresa` (string, opcional)  
  - `nif` (string, opcional)  
  - `mes` (string, opcional) — usado também no nome do ficheiro gerado  
- **`entries`** (lista, obrigatória; pode ser vazia): cada item é uma linha  
  - `day` (inteiro ou string, opcional)  
  - `description` (string, opcional)  
  - `location` (string, opcional)  
  - `start_time` (string, opcional)  
  - `end_time` (string, opcional)  
  - `percentagem` (inteiro, opcional): percentagem de 0 a 100  

Campos desconhecidos são **ignorados**. Valores em falta aparecem em branco no Excel.

**Exemplo mínimo:**

```json
{
  "meta": {},
  "entries": []
}
```

**Exemplo completo:**

```json
{
  "meta": {
    "empresa": "Minha Empresa",
    "nif": "123456789",
    "mes": "Março 2026"
  },
  "entries": [
    {
      "day": 1,
      "description": "Reunião",
      "location": "Escritório",
      "start_time": "09:00",
      "end_time": "10:00",
      "percentagem": 75
    }
  ]
}
```

### Enviar o POST com `curl`

Gravar o Excel num ficheiro:

```bash
curl -X POST http://localhost:8000/generate-excel \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {
      "empresa": "Teste",
      "nif": "PT123",
      "mes": "Março 2026"
    },
    "entries": [
      {
        "day": 1,
        "description": "Atividade",
        "location": "Remoto",
        "start_time": "09:00",
        "end_time": "12:00",
        "percentagem": 100
      }
    ]
  }' \
  -o relatorio.xlsx
```

### Enviar o POST com ficheiro JSON

```bash
curl -X POST http://localhost:8000/generate-excel \
  -H "Content-Type: application/json" \
  -d @payload.json \
  -o relatorio.xlsx
```

### Resposta em caso de sucesso

- Código **200**
- Corpo: binário **XLSX**
- Nome sugerido no cabeçalho: `relatorio_<mes>_<timestamp_utc>.xlsx` (o `mes` é sanitizado para o nome do ficheiro)

### Erros comuns

- **400**: corpo inválido (falta `meta`, etc.) — resposta JSON com detalhes de validação  
- **500**: template ou mapeamentos em falta / inválidos — resposta JSON com mensagem de erro  

## Configuração

Variáveis de ambiente (opcionais; valores por omissão relativos à pasta de trabalho atual):

| Variável               | Descrição |
|------------------------|-----------|
| `TEMPLATE_PATH`        | Caminho para o `.xlsx` modelo (predefinição: `templates/excel_template.xlsx`) |
| `HEADER_MAPPING_PATH`  | JSON que mapeia `meta` para células (predefinição: `templates/mappings/header_mapping.json`) |
| `ROWS_MAPPING_PATH`    | JSON que define linhas e colunas das entradas (predefinição: `templates/mappings/rows_mapping.json`) |
| `LOG_LEVEL`            | Nível de log (ex.: `INFO`) |

Para usar outro modelo, por exemplo `templates/excel_template2.xlsx`:

```bash
export TEMPLATE_PATH=templates/excel_template2.xlsx
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Testes

```bash
uv run pytest
```

Ou: `make test`.

## Documentação adicional

- Guia rápido detalhado: [specs/002-generate-excel-from-json/quickstart.md](specs/002-generate-excel-from-json/quickstart.md)
