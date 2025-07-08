# ADR-001: Mixed SQLAlchemy Mapping Strategy

## Status
Accepted

## Context
Our codebase includes both:
- **Rich domain modules** with significant business logic, requiring testability and clear separation of concerns.
- **Anemic modules** where entities serve primarily as data containers and follow a CRUD-oriented access pattern.

SQLAlchemy provides two primary ORM mapping styles:
- **Declarative Mapping**: A concise way to define both the schema and model in a single class, ideal for simple, CRUD-based entities.
- **Imperative (Classical) Mapping**: Separates the Python class from its database table mapping, allowing models to remain free from any ORM dependencies.

We aim to adhere to **clean architecture principles**, favoring **domain purity** and **testability** for rich domain logic, 
while maintaining **developer ergonomics** and **simplicity** in CRUD modules.

## Decision
We will adopt the following mapping strategy:
- Use **imperative (classical) mapping** for modules with **rich domain models**:
  - Domain entities will be **pure Python classes** (using `attrs` package), decoupled from the ORM.
  - SQLAlchemy mapping will be done via `registry().map_imperatively(...)` in a dedicated persistence layer.
  - This supports unit testing, domain isolation, and DDD-friendly patterns.

- Use **declarative mapping** for **anemic or CRUD-style modules**:
  - Models will inherit from a shared `Base` class using `declarative_base()` or `registry().generate_base()`.
  - This reduces boilerplate and is suitable for modules without domain logic (e.g. logs, reference tables, lookup data).

## Consequences

### Benefits
- **Pure, testable domain code** in rich modules.
- Clear **separation of domain and infrastructure** concerns.
- Maintains **developer efficiency** where full separation is unnecessary.
- Supports **hybrid project architecture**, balancing flexibility and clarity.

### Drawbacks
- Developers must be familiar with **both mapping styles**.
- Imperative mapping requires **more boilerplate** and setup.
- Slightly more complex tooling (e.g., ensuring metadata consistency across mapping styles).

## Alternatives Considered
- **Using only declarative mapping**: Simpler, but would couple domain models to the ORM and reduce testability.
- **Using only imperative mapping**: Ensures consistency, but increases boilerplate even in simple cases.

## Implementation Notes
- Use a **shared `MetaData` and `registry`** to avoid conflicts across mapping styles.
