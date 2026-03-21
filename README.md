# Excel API

API **FastAPI** que gera ficheiros Excel (`.xlsx`) a partir de JSON: relatórios **Mapa Diário** (`/reports/mapa-diario`) e **Mapa KM** (`/reports/mapa-km`). O **Mapa Diário** substitui o antigo `/generate-excel`: realce na **coluna A** (dias do mês) para fins de semana e feriados, percentagens no modelo, rodapé com último dia útil, e nome de ficheiro `relatorio_<mês>_<timestamp_utc>.xlsx`.

## Requisitos

- Python **3.11** ou superior
- [uv](https://docs.astral.sh/uv/) (gestor de dependências e ambiente)
- Modelos `.xlsx` e JSON de mapeamento em `src/reports/mapa_diario/` e `src/reports/mapa_km/` (ver [Configuração](#configuração))

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

## Endpoints

| Método | URL | Corpo | Resposta (sucesso) |
|--------|-----|-------|---------------------|
| `GET` | `/health` | — | JSON (estado do serviço) |
| `GET` | `/docs` | — | Swagger UI (documentação interativa) |
| `GET` | `/openapi.json` | — | Schema OpenAPI (JSON) |
| `POST` | `/reports/mapa-diario` | JSON | Ficheiro `.xlsx` (binário) |
| `POST` | `/reports/mapa-km` | JSON | Ficheiro `.xlsx` (binário) |

**Cabeçalho obrigatório nos POST:** `Content-Type: application/json`

---

### `GET /health`

Verificação de saúde do serviço.

**Exemplo de resposta (200):**

```json
{
  "status": "healthy",
  "service": "excel-generation-api"
}
```

---

### `GET /docs` e `GET /openapi.json`

Documentação interativa (Swagger) e schema OpenAPI gerados pelo FastAPI.

---

### `POST /reports/mapa-diario`

Gera o relatório **Mapa Diário** (modelo em `src/reports/mapa_diario/template.xlsx`, mapeamento em `mapping.json`). Comportamento alinhado com o antigo `/generate-excel`: cabeçalho, linhas, rodapé (incl. último dia útil), percentagens como **%** com realce se &lt; 100%, realce na coluna A (feriado &gt; fim de semana), `holidays` com valores **1–31** inválidos **ignorados**, campos extra **ignorados**.

- **`meta.mes`:** inteiro **1–12** (obrigatório).
- **`funcionario`:** opcional (rodapé do mapa diário).

**Exemplo mínimo:**

```json
{
  "meta": { "mes": 3 },
  "entries": [],
  "holidays": [25]
}
```

**Exemplo completo:**

```json
{
  "meta": {
    "empresa": "Minha Empresa",
    "nif": "123456789",
    "mes": 3
  },
  "entries": [
    {
      "day": 1,
      "description": "Reunião",
      "location": "Escritório",
      "start_time": "09:00",
      "end_time": "10:00",
      "percentagem": 100
    }
  ],
  "funcionario": {
    "nome_completo": "João Costa",
    "morada": "Av. Central 50",
    "nif": "222333444"
  },
  "holidays": [5, 25]
}
```

**`curl`:**

```bash
curl -X POST http://localhost:8000/reports/mapa-diario \
  -H "Content-Type: application/json" \
  -d '{
    "meta": { "empresa": "Teste", "mes": 3 },
    "entries": [{ "day": 1, "description": "Atividade", "percentagem": 100 }],
    "holidays": [25]
  }' \
  -o mapa_diario.xlsx
```

**Resposta em sucesso:** código **200**, ficheiro **XLSX**, nome sugerido: `relatorio_<mes>_<timestamp_utc>.xlsx` (ex.: `relatorio_3_20260321T120000Z.xlsx`).

---

### `POST /reports/mapa-km`

Gera o relatório **Mapa KM** (modelo em `src/reports/mapa_km/`).

- **`meta.mes`:** string com o **nome do mês em português** (obrigatório): `Janeiro`, `Fevereiro`, `Março`, `Abril`, `Maio`, `Junho`, `Julho`, `Agosto`, `Setembro`, `Outubro`, `Novembro`, `Dezembro`.
- **`vehicle`** (opcional): dados do veículo no rodapé — `modelo`, `matricula` (strings), `kms` (inteiro, opcional).
- **`holidays`:** lista de inteiros **1–31** (valores inválidos são ignorados, como no mapa diário).

**Exemplo mínimo:**

```json
{
  "meta": { "mes": "Março" },
  "entries": [],
  "holidays": [25]
}
```

**Exemplo completo:**

```json
{
  "meta": {
    "empresa": "Minha Empresa",
    "nif": "123456789",
    "mes": "Março"
  },
  "entries": [
    {
      "day": 1,
      "description": "Deslocação cliente",
      "location": "Porto",
      "start_time": "09:00",
      "end_time": "12:00",
      "percentagem": 100
    }
  ],
  "vehicle": {
    "modelo": "Citroën C3",
    "matricula": "AA-12-BB",
    "kms": 45000
  },
  "holidays": [5, 25]
}
```

**`curl`:**

```bash
curl -X POST http://localhost:8000/reports/mapa-km \
  -H "Content-Type: application/json" \
  -d '{
    "meta": { "empresa": "Teste", "mes": "Março" },
    "entries": [{ "day": 1, "description": "Viagem", "percentagem": 100 }],
    "vehicle": { "modelo": "Carro X", "matricula": "BB-99-CC" },
    "holidays": [25]
  }' \
  -o mapa_km.xlsx
```

**Resposta em sucesso:** código **200**, ficheiro **XLSX**, nome sugerido: `relatorio_<número_do_mês>_<timestamp_utc>.xlsx` (mês **1–12** no nome do ficheiro, para cabeçalhos HTTP ASCII).

---

## Erros comuns

- **422**: corpo JSON que não cumpre o modelo (ex.: `meta` em falta, `meta.mes` inválido) — resposta JSON de validação  
- **500**: falha ao gerar o ficheiro (template, processamento) — resposta JSON com `error`, `message`, `status`  

## Configuração

Cada relatório usa um **template** `.xlsx` e um **`mapping.json`** em `src/reports/<módulo>/`. As constantes de cor (fins de semana, feriados, percentagem &lt; 100%) estão em `src/core/config.py`.

| Variável    | Descrição |
|-------------|-----------|
| `LOG_LEVEL` | Nível de log (ex.: `INFO`) |

## Testes

```bash
uv run pytest
```

Ou: `make test`.

## Documentação adicional

- Realce de fins de semana e feriados: [specs/003-weekend-highlighting/spec.md](specs/003-weekend-highlighting/spec.md)
- API de relatórios Mapa Diário / Mapa KM: [specs/004-excel-reports-api/quickstart.md](specs/004-excel-reports-api/quickstart.md)
