<!--
Sync Impact Report
- Version change: N/A → 1.0.0
- Modified principles:
  - [PRINCIPLE_1_NAME] → JSON Source of Truth
  - [PRINCIPLE_2_NAME] → Template-Driven Excel Generation
  - [PRINCIPLE_3_NAME] → Structured Fixed + Dynamic Mapping
  - [PRINCIPLE_4_NAME] → Preserve Excel Semantics and Style
  - [PRINCIPLE_5_NAME] → Determinism and Statelessness
- Added sections: Non-goals & Constraints, Development Workflow
- Removed sections: no structural removals (template placeholders resolved)
- Templates requiring updates: .specify/templates/plan-template.md ✅ reviewed, no edits required; .specify/templates/spec-template.md ✅ reviewed, no edits required; .specify/templates/tasks-template.md ✅ reviewed, no edits required
- Follow-up TODOs: none
-->

# Excel Template Service Constitution

## Core Principles

### 1. JSON is the source of truth
The service MUST accept structured JSON input as the only authoritative payload. All transformations, validation and mapping MUST be derived from this JSON, not from ad hoc runtime state or file-internal metadata.

### 2. Template-driven Excel generation (no in-place mutation)
Excel output MUST be generated from a clean read-only model of a predefined XLSX template on each request. The system MUST NOT open an existing generated file and mutate it; every output is a fresh file derived from template + mapping + input.

### 3. Support fixed header fields and dynamic tabular rows
Mapping MUST support:
- fixed fields (header → fixed template cells)
- dynamic rows (data arrays → execution row + column mapping)

### 4. Preserve formulas and formatting
The pipeline MUST preserve all original template cells, including formulas, cell styles, number formats, merged ranges, and conditional formatting, while only injecting values where mapping explicitly says so.

### 5. Explicit static/dynamic mapping contract
Mapping contracts MUST clearly distinguish static cell targets and dynamic row table ranges. Behavioral guarantees:
- static fields are one-to-one to fixed cell addresses
- dynamic rows are expanded from a designated start row and column set
- unbound or unused cells remain unchanged

### 6. Deterministic output
Given the same JSON input + template + mapping config, the service MUST produce bitwise consistent Excel output across runs, independent of request timing or non-deterministic system state.

### 7. Statelessness
The service MUST be stateless. No in-memory session state may affect results. All request context is derived from request payload and template files. Any caching MUST be safe and replicate-only, does not affect correctness.

### 8. Clean, minimal, production-ready code
Implementation MUST follow clean architecture patterns, use minimal dependencies, and include tests, type validation, and error handling. Production readiness requires logging, error semantics, and clear extension points.

## Non-goals & Constraints
- No authentication frameworks or authorization checks.
- No database persistence for templates or generated files.
- No local filesystem persistence of generated outputs in the core service flow (files are streamed responses).

Technology constraints:
- Python 3.11+
- FastAPI for HTTP API
- openpyxl for Excel template handling

Non-goals:
- No PDF conversion, no spreadsheet viewers, no scheduling subsystem.

## Development Workflow
- Every change MUST include unit tests for JSON mapping, template selection, and formula/formatting preservation.
- Maintain a CI gate that fails on non-deterministic output or missing mapping contract coverage.
- Use code review checklists anchored to this constitution: JSON source-of-truth, template immutability, statelessness, and deterministic behavior.
- Any feature expansion MUST introduce or update a principle section and include corresponding spec tasks.

## Governance
- This constitution is the project's guiding agreement. All design docs, plans, and implementation tasks must trace back to these principles.
- Amendments require a PR with:
  1. Updated constitution text
  2. Rationale for change (backward compatibility impact)
  3. Incremented version according to semantic rules
  4. A migration plan for affected artifacts (templates, tests, docs)
- Versioning policy:
  - MAJOR for fundamental principle changes or removals
  - MINOR for new principles or mandatory sections
  - PATCH for clarifications and wording improvements
- Compliance review schedule:
  - quarterly team review of Constitution alignment
  - immediate reassessment for any feature that touches template generation mechanics

**Version**: 1.0.0 | **Ratified**: 2026-03-20 | **Last Amended**: 2026-03-20
