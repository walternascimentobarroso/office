<!--
Sync Impact Report
- Version change: 2.0.0 → 3.0.0
- Modified principles: Added explicit API contract principles for domain naming, company metadata, top-level month, structure consistency, English naming, and future-proof extensibility.
- Added principles: API Contract Explicit Domain Naming, Company Metadata, Top-Level Month Field, Consistent Base Request Structure, English Naming Policy, Future-Proof Contract Evolution
- Added sections: none
- Removed sections: none
- Templates requiring updates: .specify/templates/plan-template.md ✅ updated (Constitution Check aligned with new principles); .specify/templates/spec-template.md ✅ reviewed, no edits required; .specify/templates/tasks-template.md ✅ reviewed, no edits required
- Follow-up TODOs: none
-->

# Excel Report Generation Backend Constitution

## Core Principles

### 1. Report Isolation and Self-Containment
Each report must be isolated and self-contained (plugin-like structure). Reports must not share business logic directly; shared logic must live in common services.

Rationale: Ensures modularity, prevents tight coupling between report types, and facilitates independent development and maintenance.

### 2. Support for Multiple Report Types
The system must support multiple report types with independent schemas and behaviors.

Rationale: Allows the system to handle diverse reporting needs without monolithic code, enabling specialization and scalability.

### 3. Consistent Excel Generation Pipeline
Excel generation must follow a consistent pipeline: load template → fill data → apply styles → return file.

Rationale: Standardizes the generation process, making it predictable, easier to debug, and maintainable across different reports.

### 4. Reusable Styling Rules
Styling rules (weekends and holidays) must be reusable across all reports.

Rationale: Promotes visual consistency, reduces code duplication, and simplifies updates to styling logic.

### 5. Deterministic Output
The system must be deterministic (same input → same output).

Rationale: Ensures reliability, testability, and trust in the generated reports.

### 6. JSON as Single Source of Truth
JSON input is the single source of truth.

Rationale: Simplifies data validation, transformation, and ensures all operations derive from a consistent data source.

### 7. Easy Extensibility
The system must be easily extensible to support new reports.

Rationale: Future-proofs the system, allowing quick addition of new report types without major refactoring.

### 8. Modular Architecture and Clear Separation of Concerns
The system must follow modular architecture with clear separation of concerns.

Rationale: Improves maintainability, testability, and scalability by organizing code into distinct, focused modules.

### 9. API Contract Explicit Domain Naming
API requests must use explicit domain naming instead of generic fields.

Rationale: Self-descriptive field names reduce ambiguity, simplify integration, and improve long-term contract clarity.

### 10. Company Metadata instead of Meta
Request payloads must replace any generic "meta" object with "company".

Rationale: Explicit company context avoids unclear semantics and aligns with business domain references.

### 11. Month as Top-Level Field
The request body must include "month" as a top-level field for all report endpoints.

Rationale: Ensures uniform report targeting and reduces nested parsing complexity.

### 12. Consistent Base Request Structure
All reports must share a consistent base request structure with mandatory top-level keys for common metadata and parameters.

Rationale: Simplifies request validation, onboarding, and supports shared middleware for pre-validation and logging.

### 13. English Naming and Consistency
Field names in requests and responses must be in English and consistent across reports.

Rationale: English naming standardizes contract usage for global teams and reduces localization mismatch errors.

### 14. Future-Proof Contract Evolution
The contract must be designed for evolution: allow additional report types, optional extensions, and safe deprecation paths.

Rationale: Supports long-term maintainability and growth without requiring disruptive refactors.

## Non-goals & Constraints

Technology constraints:
- Python 3.11+
- FastAPI
- openpyxl

Non-goals:
- No database (for now)
- No authentication
- No async complexity unless necessary
- Backward compatibility is not required (breaking change allowed for API contract updates)

## Development Workflow

- Implement modular architecture with clear separation of concerns: reports as plugins, shared services for common logic, dedicated modules for Excel generation pipeline.
- Ensure each report type has independent schemas, behaviors, and test suites.
- Maintain deterministic behavior through comprehensive testing and input validation.
- Use JSON schemas for input validation and documentation.
- Follow the consistent Excel generation pipeline in all report implementations.
- Promote reusability of styling rules through centralized configuration and services.
- Enforce API contract standards in shared validation and contract tests.
- Validate that all endpoints require top-level "month"; according to rules, payload fields must use explicit domain naming and company metadata.
- Maintain English naming conventions globally for request and response models.

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
  - immediate reassessment for any feature that touches report generation mechanics

**Version**: 3.0.0 | **Ratified**: 2026-03-20 | **Last Amended**: 2026-03-22
