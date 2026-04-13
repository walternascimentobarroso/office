# Backend — Ativos (Assets) — *Office API*

Implementar o **backend REST** para **ativos/equipamentos** neste repositório (**FastAPI**, SQLAlchemy async, Alembic), alinhado ao contrato esperado pelo frontend (`lib/assets/types.ts`), mas com **nomes de campos em snake_case** nos schemas Pydantic/OpenAPI (mapear camelCase ↔ snake_case na integração do frontend).

---

## Contexto do projeto (obrigatório)

Seguir a arquitetura já usada aqui:

| Camada | Responsabilidade |
|--------|------------------|
| **Router** (`app/api/routers/`) | Orquestração: validação Pydantic, dependências, chamar service, devolver resposta. **Sem** lógica de negócio nem acesso direto à BD. |
| **Service** (`app/services/`) | Toda a lógica de negócio; não depender de detalhes do FastAPI além do necessário. |
| **Repository** (`app/repositories/`) | Apenas acesso a dados; reutilizar padrões de `BaseRepository` quando existir. |
| **Schemas** (`app/schemas/`) | Modelos Pydantic (create/update/read). |
| **Model** (`app/models/`) | ORM: `UUIDPrimaryKeyMixin`, `TimestampMixin`, `company_id` → `companies.id`, soft delete (`deleted_at`) como nas outras entidades. |

- **Multi-tenant:** cada ativo pertence a uma **empresa** (`company_id`), como `Employee` e rotas sob `/companies/{company_id}/...`.
- **Autenticação / autorização:** usar `get_current_user` e `require_company_access` nos routers aninhados em empresa (ver `app/api/routers/employees.py`). Utilizadores com role `admin` podem aceder fora do `company_id` do token conforme a regra já definida em `require_company_access`.
- **Permissões de escrita:** alinhar com recursos similares (ex.: `employees`: mutações restritas a `require_roles("admin")` onde fizer sentido); documentar na implementação se leitura é para qualquer utilizador autenticado com acesso à empresa.

---

## Modelo de domínio (referência)

Tipos alinhados ao frontend; **na API REST usar snake_case** e corrigir typos do legado:

| Conceito frontend | Campo API (snake_case) |
|-------------------|-------------------------|
| `purchas_date` | `purchase_date` (data ISO `YYYY-MM-DD` ou datetime com timezone) |
| `serial_n_umber` | `serial_number` |
| `invoiceFile` | `invoice_file_url` ou `invoice_storage_key` (apenas referência; ver upload) |

Enums:

- `category`: `mine` \| `landlord` \| `supplier`
- `status`: `active` \| `maintenance` \| `broken` \| `disposed`

Campos principais:

- `id` — UUID  
- `name` — obrigatório  
- `description` — opcional  
- `price` — numérico ≥ 0  
- `category`, `status` — enums  
- `location`, `purchase_date`, `warranty_until`, `serial_number`, `brand`, `notes` — opcionais conforme modelo  
- `created_at`, `updated_at`, `deleted_at` — auditoria (mixins existentes)  
- Ficheiro de fatura: **não** persistir Base64 na BD; guardar URL ou identificador de objeto após upload (ver abaixo).

---

## Requisitos funcionais

1. **CRUD completo** por empresa:
   - listar com **paginação**, **filtros** e **ordenação**;
   - obter um por id;
   - criar, atualizar (`PATCH`), eliminar (preferir **soft delete** coerente com o resto do projeto).

2. **Escopo:** todas as queries e mutações devem respeitar `company_id` no path e as regras de `require_company_access` / token.

3. **Ficheiro de nota fiscal:** aceitar **upload multipart** num endpoint dedicado; persistir em **object storage** (S3/MinIO ou equivalente) e guardar na BD apenas **URL pública/presigned** ou **chave de objeto** — **nunca** Base64 em coluna.  
   *Nota:* este repositório **não expõe ainda** um módulo genérico de upload para storage; a implementação deve introduzir um cliente/config mínimo (variáveis em `.env` / `.env.example`) e um serviço reutilizável, sem duplicar lógica entre router e service.

4. **Validação:** nome obrigatório; preço ≥ 0; enums fixos para `category` e `status`; datas opcionais válidas.

5. **Segurança:** todas as rotas autenticadas; utilizador só acede aos ativos no contexto da empresa (e regra `admin` já existente).

---

## Paginação e resposta de lista

Usar o schema existente `Page[T]` em `app/schemas/pagination.py`:

- Query: `limit` (default 50, máx. 200), `offset` (default 0) — **não** usar `page` / `pageSize` a menos que se normalize internamente para `limit`/`offset`.
- Resposta: `items`, `total`, `limit`, `offset`.

Filtros/ordenação sugeridos (ajustar nomes aos query params do projeto):

- `search` — texto em nome (e opcionalmente descrição/marca/localização);
- `category`, `status`, `location`;
- `sort` — formato explícito no OpenAPI (ex.: `created_at:desc`, `price:asc`) ou parâmetros separados `sort_by` + `sort_order`, desde que documentado.

---

## API (ajustada ao estilo deste backend)

Prefixo aninhado por empresa (espelhar `employees`):

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `GET` | `/companies/{company_id}/assets` | Lista paginada + filtros + ordenação |
| `GET` | `/companies/{company_id}/assets/{asset_id}` | Detalhe |
| `POST` | `/companies/{company_id}/assets` | Criar (JSON) |
| `PATCH` | `/companies/{company_id}/assets/{asset_id}` | Atualização parcial |
| `DELETE` | `/companies/{company_id}/assets/{asset_id}` | Eliminar (soft delete) |
| `POST` | `/companies/{company_id}/assets/{asset_id}/invoice` | Upload multipart do ficheiro de fatura (atualiza referência no ativo) |

Registrar o router em `src/main.py` (ou no agregador de routers já usado pela aplicação).

---

## Migrações e testes

- Nova migration Alembic para a tabela de ativos (índices em `company_id`, filtros frequentes, unicidade apenas se for requisito de negócio).
- Testes (pytest) ao nível de service/repository conforme o padrão do repositório; validar regras de escopo e validação.

---

## Fora de âmbito (tarefas separadas)

- Alterar o frontend para deixar de usar apenas `LocalStorage` (`office_assets`) e passar a consumir esta API (integração e mapeamento camelCase/snake_case).

---

## Critérios de aceitação

- [ ] Rotas finas; lógica em services; dados em repositories.
- [ ] `company_id` obrigatório e consistente com FK e `require_company_access`.
- [ ] Lista com `Page` (`limit`/`offset`) e filtros/ordenação acordados.
- [ ] Upload de fatura sem Base64 na BD; referência persistida de forma segura.
- [ ] Código **Ruff-clean** e alinhado às regras do projeto (SOLID, camadas).
