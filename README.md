# Fullstack-Dev-Test-Task

This is a task to test potential candidate skills in Python + SQL + TypeScript.

- **Assignment**: Add Role-Aware Access + Architecture Decisions + **Run the app**
- **Timebox**: Aim for up to 1 hour. If you cut scope, say what you cut and why.


## Table of Contents

- [Goal](#goal)
- [Base Template](#base-template)
- [Suggested Time Allocation](#suggested-time-allocation)
- [Requirements](#requirements)
  - [1. Clone the Base Template](#1-clone-the-base-template)
  - [2. Roles and Authorization Surface](#2-roles-and-authorization-surface)
  - [3. Code Quality Expectations](#3-code-quality-expectations)
  - [4. Architecture & Documentation](#4-architecture--documentation)
  - [5. Non-Functional Requirements](#5-non-functional-requirements)
  - [6. UX Behavior](#6-ux-behavior)
  - [7. Developer UX](#7-developer-ux)
- [Constraints](#constraints)
- [What We Review](#what-we-review)
- [Submission](#submission)

## Goal

Add role-based access control (RBAC) to the existing Full-Stack FastAPI Template so that only authorized users can access sensitive endpoints and UI sections.

**We prioritize clean, maintainable code over comprehensive test coverage or extensive documentation.**

You may reuse any libraries already in the template.

> **Note**: RBAC can be implemented with simple role checks or a small policy layer. Keep scope tight. Favor clarity over cleverness.

## Base Template

**Tech Stack**:
- **Backend**: FastAPI / SQLModel / PostgreSQL
- **Frontend**: React / TypeScript

**Repository**: [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template/tree/master)

## Suggested Time Allocation

How we believe it is doable in a 1-hour timebox:

| Activity | Time           | Priority |
|----------|----------------|----------|
| Understanding the codebase | 15 min         | High |
| Implementation (clear, maintainable code) | 25 mins | **Critical** |
| Testing (focused, critical paths) | 10 min         | High |
| Documentation (README updates) | 10 min         | Medium |

**If running short on time:**
- ✓ **Prioritize**: Clear, working authorization code with consistent patterns
- ✓ **Then**: 3-5 well-chosen tests covering critical scenarios
- ⚠ **Cut if needed**: Extra features, comprehensive test coverage, diagrams
- ❌ **Don't cut**: Security checks, README setup instructions

## Requirements

### 1. Clone the Base Template

Clone the repository: https://github.com/fastapi/full-stack-fastapi-template/tree/master

### 2. Roles and Authorization Surface

#### Implement the Following Roles

| Role | Permissions |
|------|-------------|
| **admin** | Full access to user management and settings |
| **manager** | Can list users and view metrics, but not change global settings |
| **member** | Can only access their own profile and basic app features |

#### Protect a Small but Realistic Surface

- List users
- Create user
- View "metrics/insights" page (simple stub is acceptable)
- View and update own profile

**Exact permission mapping is up to you.**

State it clearly in your docs and enforce it consistently in the backend and frontend.

#### Permission Matrix

| Action | admin | manager | member |
|--------|-------|---------|--------|
| List all users | ✓ | ✓ | ✗ |
| Create user | ✓ | ✗ | ✗ |
| View metrics | ✓ | ✓ | ✗ |
| Update own profile | ✓ | ✓ | ✓ |
| Update any profile | ✓ | ✗ | ✗ |

This is the permission mapping implemented in the application.

### 3. Code Quality Expectations

**We prioritize maintainable, readable code over clever solutions.**
 
- **Clear naming**: Function/variable names that explain intent without comments
- **Single responsibility**: Small, focused functions
- **Easy to extend**: Adding a new role shouldn't require touching 10+ files
- **Self-documenting**: Code structure makes the authorization model obvious

> **Key principle**: A teammate should understand your authorization model in 5 minutes by reading your code.

### 4. Architecture & Documentation

Document your implementation approach clearly but concisely.

#### Required

- [x] **Permission matrix** in README showing which role can access what
- [x] **Brief explanation** of the authorization approach:
  - Where authorization checks live (middleware, dependencies, decorators?)
  - How roles are stored and validated
  - How frontend learns about user capabilities
- [x] **Inline code comments** only for non-obvious authorization logic

Backend authorization is enforced at route boundaries through the dependency functions in `backend/app/api/deps.py`. User listing and metrics require manager or admin, while creating or changing another user (including their role) requires admin. Authenticated users can view and update their own profile. Denied API requests return HTTP 403.

Roles are stored on the user as the `Role` enum (`admin`, `manager`, or `member`). The CRUD layer synchronizes admin with the legacy `is_superuser` flag, and the migration backfills existing superusers to the admin role. The initial account configured by `FIRST_SUPERUSER` is created as an admin.

The frontend reads the role from the authenticated user response. Shared helpers in `frontend/src/utils/roles.ts` drive navigation visibility and route guards; unauthorized direct navigation leads to a friendly `/forbidden` page. Backend authorization remains authoritative even when a link is hidden in the UI.

#### Optional (Bonus Points)

- [ ] **1-2 Architecture Decision Records (ADRs)** for your most critical decisions
  - Use any simple ADR format (problem, options, decision, trade-offs)
  - 200-400 words each
  - Example topics: Why you chose your authorization pattern, where checks live, how the frontend handles permissions
- [ ] **Simple diagram** showing where auth/authz checks happen
  - Mermaid, C4-style, or hand-drawn PNG is fine

**Philosophy**: We value clear thinking over formal documentation. 
Your code should clearly explain your approach; that's usually sufficient.
RBAC implementation, though, usually has at least a few options to implement, hence an additional README will add value.

### 5. Non-Functional Requirements

Demonstrate you considered real-world constraints:

#### 1. Maintainability (Critical)

- Keep coupling low; use consistent patterns
- A teammate should understand your authorization logic in 5 minutes

#### 2. Testability (Important)

- Provide **focused backend tests** covering critical authorization paths

> **Note**: Tests are required, but we prioritize **quality over quantity**. 3 well-chosen tests with clean code beat 20 tests with spaghetti code.

### 3. UX Behavior

- **The UI** should:
  - Hide navigation links/buttons that the user can't access
  - Show a friendly "Forbidden" or "Access Denied" message if navigating directly to unauthorized routes
  - Not just fail silently or show cryptic errors

### 4. Developer UX

Update the README with:

- **How to run locally** (setup, dependencies, database)
- **How to seed test data** with at least one admin and one non-admin user
- **How to run tests**
- **Database migrations** for any schema changes (if applicable)

Make it easy for us to run your solution without hunting for setup instructions.

#### Local setup

1. Set local values in `.env`, including `SECRET_KEY`, `POSTGRES_PASSWORD`, and `FIRST_SUPERUSER_PASSWORD`.
2. Start PostgreSQL and Mailpit: `docker compose up -d db mailpit`.
3. From `backend/`, install dependencies and prepare the database: `uv sync && uv run bash scripts/prestart.sh`.
4. Start the API from `backend/`: `uv run fastapi dev`.
5. From the repository root, install frontend dependencies: `bun install`.
6. Start the frontend from the root: `bun run dev`.

The initial admin uses `FIRST_SUPERUSER` and `FIRST_SUPERUSER_PASSWORD` and is created when the database is initialized. To seed a non-admin user, open the app's **Sign up** page and register an account; public signup always creates a member. An admin can also create or edit users and select member, manager, or admin; the creation role defaults to member. The API accepts a `role` value on `POST /api/v1/users/`.

Run the focused backend tests with `cd backend && uv run pytest tests/api/routes/test_users.py -q`; build the frontend with `cd frontend && npm run build`. The Alembic migration `6a2b3c4d5e6f` adds the role column and backfills existing superusers. `scripts/prestart.sh` applies migrations and initializes the admin account.

## What We Review

### Primary Criteria (60%)

**Code readability and maintainability**
- ✓ Clear separation of concerns
- ✓ Consistent authorization patterns
- ✓ Self-documenting code structure
- ✓ Low coupling between components
- ✓ Easy to understand and extend

**Working RBAC implementation**
- ✓ Consistent enforcement in backend and frontend
- ✓ No obvious security gaps or privilege escalation
- ✓ Correct HTTP status codes and error handling

### Secondary Criteria (30%)

**Test coverage**
- ✓ Focused tests on critical authorization paths
- ✓ Both allowed and denied scenarios tested
- ✓ Tests are clear and well-named

**Setup and documentation**
- ✓ Setup instructions work on first try
- ✓ Clear explanation of authorization approach
- ✓ Permission matrix documented

### Nice to Have (10%)

- Thoughtful UX for forbidden states
- Observability (logging denied attempts)
- Architecture Decision Records (ADRs)
- Helpful diagrams
- Extra polish

> **Philosophy**: We're evaluating your ability to write production-quality code under time constraints. We'd rather hire someone who delivers clean, working code with good tests than someone who delivers everything but it's hard to maintain.

## Submission

**Deliverables**:

- [ ] PR or repo link with commit history
- [ ] Updated README with:
  - Setup instructions
  - Permission matrix
  - Brief explanation of your approach
- [ ] Backend tests covering critical authorization scenarios
- [ ] Working implementation of RBAC
- [ ] Optional: `NOTES.md` with anything you want us to know (scope cuts, trade-offs, what you'd do with more time)

---

**Good luck!** Focus on demonstrating clear thinking and solid engineering fundamentals. We're looking for maintainable code, not perfect code.
