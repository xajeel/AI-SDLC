---
name: understand-codebase
description: "Analyze, explain, and navigate any codebase from scratch. Use when: user shares a codebase, uploads files, pastes code, asks to understand a project, asks how code works, wants architecture overview, needs onboarding guide, asks about project structure, database schema, or application flow. Works with any language, framework, or project type."
argument-hint: "Optionally specify a focus area: 'auth system', 'database layer', 'frontend routing', etc."
---

# Understand Any Codebase

Produce a comprehensive, beginner-friendly walkthrough of a codebase. Treat the reader as a smart 12th-grade student who knows basic programming but has never seen this project before. Use simple language, relatable analogies, and never assume familiarity with the specific framework or architecture.

## Before You Begin

1. **Assess scope.** If the codebase is very large (monorepo, many services), ask the user:
   - "This is a large codebase. Want me to start with a high-level overview, or focus on a specific area first?"
   - Offer to break the analysis into chunks (e.g., backend first, then frontend).
2. **Gather context.** Read the project root: README, package files, config files, entry points, and folder structure. Use search tools liberally to understand the full picture before writing anything.
3. **Detect the stack.** Identify languages, frameworks, package managers, databases, and external services from config files (package.json, pyproject.toml, Cargo.toml, go.mod, Gemfile, docker-compose.yml, etc.).

## Output Sections

Produce each section below in order. Use the exact heading names. If a section doesn't apply (e.g., no database), state that and skip it.

---

### 1. APPLICATION OVERVIEW

Explain in 3–5 sentences:
- What the app does in plain English (imagine explaining to a friend)
- Type of application (web app, REST API, CLI tool, mobile app, library, etc.)
- Tech stack with a one-line reason for each technology

Format:
```
## 1. Application Overview

**What it does:** [Plain English description]

**Type:** [web app / REST API / CLI / mobile / library / monorepo / etc.]

**Tech Stack:**
| Technology   | Role                  | Why it's used                     |
|--------------|-----------------------|-----------------------------------|
| Python 3.11  | Backend language      | Async support, rich ecosystem     |
| FastAPI      | Web framework         | Fast, auto-generates API docs     |
| PostgreSQL   | Database              | Relational data with JSONB support|
| React        | Frontend framework    | Component-based UI                |
```

---

### 2. PROJECT STRUCTURE

Print the full folder/file tree using ASCII art. Annotate every folder and every key file with a short description.

Format:
```
## 2. Project Structure

├── src/                    # All application source code
│   ├── api/                # REST API route handlers
│   │   ├── routes/         # One file per resource (users, posts, etc.)
│   │   └── middleware/     # Auth checks, logging, rate limiting
│   ├── models/             # Database table definitions (ORM models)
│   ├── services/           # Business logic (the "brain" of the app)
│   └── utils/              # Shared helper functions
├── tests/                  # Automated tests
├── migrations/             # Database schema change scripts
├── docker-compose.yml      # Runs the app + database in containers
├── package.json            # Dependencies and scripts (Node.js)
└── README.md               # Project documentation
```

Rules:
- Show ALL folders, but only key files (skip auto-generated or boilerplate files like `__pycache__`, `node_modules`, `.DS_Store`)
- Every line gets a `# comment` explaining its purpose
- Group related items visually

---

### 3. ARCHITECTURE DIAGRAM

Draw an ASCII diagram showing all major components/layers and how they connect. Then explain each layer in 1–2 sentences.

Format:
```
## 3. Architecture Diagram

┌─────────────┐     HTTP      ┌──────────────┐     SQL       ┌────────────┐
│   Browser   │ ─────────────>│   Backend    │ ────────────>│  Database  │
│  (React UI) │<─────────────│  (FastAPI)   │<────────────│ (PostgreSQL)│
└─────────────┘    JSON       └──────┬───────┘    Results    └────────────┘
                                     │
                                     │ API calls
                                     ▼
                              ┌──────────────┐
                              │  External    │
                              │  Services    │
                              │ (Twilio, S3) │
                              └──────────────┘

**Browser (React UI):** What the user sees and interacts with.
**Backend (FastAPI):** Receives requests, runs business logic, talks to DB.
**Database (PostgreSQL):** Stores all persistent data (users, orders, etc.).
**External Services:** Third-party APIs the app depends on.
```

Rules:
- Use box-drawing characters: `┌ ┐ └ ┘ │ ─ ┬ ┴ ├ ┤ ▼ ▲ ◄ ►`
- Label every arrow with what travels along it (HTTP, SQL, gRPC, events, etc.)
- After the diagram, explain each box in plain English

---

### 4. APPLICATION FLOW

Show where the app starts and how data moves from input to output.

Format:
```
## 4. Application Flow

**Entry Point:** `main.py` → calls `create_app()` → starts the server on port 8000

**Request Lifecycle (example: user login):**

  User types email + password
       │
       ▼
  POST /api/auth/login
       │
       ▼
  Route handler (routes/auth.py)
       │
       ▼
  Interactor validates credentials (interactors/auth.py)
       │
       ▼
  Database lookup: find user by email (models/user.py)
       │
       ▼
  Password hash comparison (services/security.py)
       │
       ▼
  Generate JWT token
       │
       ▼
  Return { token, user } to browser
```

Rules:
- Always start from the entry point file
- Pick 1–2 representative flows and trace them end-to-end
- Name the actual files involved at each step

---

### 5. USER FLOW

Map what a user can do in the app with step-by-step journeys.

Format:
```
## 5. User Flow

**Available Actions:**
1. Sign up / Log in
2. Create a new project
3. Invite team members
4. View dashboard

**Key Journey: New User Onboarding**

  Visit website
       │
       ▼
  Click "Sign Up" → Fill form → Submit
       │
       ▼
  Receive confirmation email → Click link
       │
       ▼
  Redirected to onboarding wizard
       │
       ▼
  Create first project → Invite team → See dashboard
```

Rules:
- List all major user actions first
- Pick 1–2 key journeys and trace them step by step
- Use the user's perspective, not the code's perspective

---

### 6. SECTION-BY-SECTION BREAKDOWN

For each logical section of the app (Auth, Dashboard, API layer, etc.):

Format:
```
## 6. Section-by-Section Breakdown

### 6.1 Authentication

**What it does:** Handles user signup, login, logout, and session management.

**Architecture:**
┌──────────┐    ┌──────────────┐    ┌──────────┐
│  Route   │───>│  Interactor  │───>│  Model   │
│ auth.py  │    │  auth.py     │    │ user.py  │
└──────────┘    └──────────────┘    └──────────┘

**Key Files:**
| File                    | Purpose                              |
|-------------------------|--------------------------------------|
| routes/auth.py          | HTTP endpoints for login/signup      |
| interactors/auth.py     | Business logic: validate, hash, token|
| models/user.py          | User database table definition       |
| services/security.py    | Password hashing, JWT creation       |

**Important Code:**
```python
# routes/auth.py, line 25
@router.post("/login")
async def login(credentials: LoginSchema):
    # This receives the user's email and password from the request body.
    # LoginSchema validates the input automatically (checks email format, etc.)
    user = await auth_interactor.authenticate(credentials)
    # authenticate() checks the password and returns the user if valid
    return {"token": create_token(user.id)}
    # create_token() generates a JWT — a signed string that proves identity
`` `

**Connects to:** User section (shares user model), Dashboard (login redirects there)
```

Rules:
- Create a subsection for every logical area you can identify
- Always include: purpose, mini architecture diagram, key files table, at least one explained code snippet
- Show how each section connects to others

---

### 7. DATABASE SCHEMA

Show all tables/models/collections, their fields, and relationships.

Format:
```
## 7. Database Schema

**Tables:**

┌──────────────────┐       ┌──────────────────┐
│      users       │       │     projects     │
├──────────────────┤       ├──────────────────┤
│ id (PK)          │──┐    │ id (PK)          │
│ email            │  │    │ name             │
│ password_hash    │  │    │ owner_id (FK)────│──┐
│ created_at       │  │    │ created_at       │  │
└──────────────────┘  │    └──────────────────┘  │
                      │                          │
                      └──────────────────────────┘
                         one user → many projects

**Field Explanations:**
| Table    | Field         | Type     | Purpose                            |
|----------|---------------|----------|------------------------------------|
| users    | id            | UUID     | Unique identifier for each user    |
| users    | email         | VARCHAR  | Login credential, must be unique   |
| users    | password_hash | VARCHAR  | Bcrypt hash (never store raw!)     |
| projects | owner_id      | UUID FK  | Links project to its creator       |

**Relationships:**
- users → projects: One-to-Many (one user owns many projects)
- projects → tasks: One-to-Many (one project has many tasks)
```

Rules:
- Draw tables as ASCII boxes with PK/FK annotations
- Show relationships with lines and labels
- Explain every field — assume the reader doesn't know why it exists
- If using a NoSQL database, show document structure instead of tables

---

### 8. KEY CONCEPTS & PATTERNS

Identify and explain design patterns, architectural patterns, and recurring code patterns.

Format:
```
## 8. Key Concepts & Patterns

**Architectural Patterns:**
- **Layered Architecture:** Code is split into Routes → Interactors → Models.
  Think of it like a restaurant: Routes = waiter (takes order), Interactors = chef
  (does the work), Models = pantry (stores ingredients).

**Design Patterns:**
- **Repository Pattern:** Database access is wrapped in repository classes.
  Instead of writing SQL everywhere, you call `user_repo.find_by_email(email)`.
- **Dependency Injection:** Services are passed into functions rather than imported
  directly. This makes testing easier (you can swap in fake services).

**Code Conventions:**
- All routes return standardized response objects
- Errors are raised as custom exceptions, caught by middleware
- Environment variables are loaded from .env via a Settings class
```

Rules:
- Use analogies to explain every pattern
- Note any conventions a new developer must follow
- Call out anything unusual or non-standard

---

### 9. WHERE TO START DEVELOPING

Give concrete, actionable guidance for a developer about to modify this codebase.

Format:
```
## 9. Where to Start Developing

**To add a new API endpoint:**
1. Create a route handler in `routes/` (copy an existing one as template)
2. Create business logic in `interactors/`
3. Add/modify models in `models/` if new data is needed
4. Register the route in `main.py`

**To add a new frontend page:**
1. Create component in `src/pages/`
2. Add route in `src/app/router.tsx`
3. Connect to API using hooks in `src/services/`

**Common entry points:**
| Task                    | Start here                |
|-------------------------|---------------------------|
| Fix a bug in the API    | routes/ → interactors/    |
| Add a database field    | models/ → migrations/     |
| Change UI layout        | src/components/           |
| Update business logic   | interactors/              |

**⚠️ Watch out for:**
- `services/security.py` — handles crypto; changes here affect all auth
- Database migrations — always test with a copy of production data
- `.env` variables — missing ones cause silent failures at runtime
```

---

## General Rules

1. **Always use ASCII art** for diagrams — never suggest Mermaid, PlantUML, or images unless the user specifically asks for them.
2. **Name real files and line numbers** — don't say "the auth file," say `routes/auth.py, line 42`.
3. **Explain code snippets line by line** — add inline comments to every non-obvious line.
4. **Use analogies** — compare technical concepts to everyday things (restaurant, library, post office, etc.).
5. **Be honest about gaps** — if you can't access a file or understand a pattern, say so and ask the user.
6. **Handle partial codebases** — if only some files are shared, analyze what you have and list what you'd need to complete the picture.
7. **Scale appropriately:**
   - Small script (< 5 files): Cover everything in one response.
   - Medium project (5–50 files): Full analysis, may need 2–3 responses.
   - Large project (50+ files): Start with overview (sections 1-3), then break remaining sections into focused follow-ups. Ask the user which sections to dive into next.
8. **Language/framework agnostic** — these instructions work for Python, JavaScript, Go, Rust, Java, Ruby, Swift, Kotlin, C#, PHP, or any other language. Adapt terminology to match the stack (e.g., "models" for ORMs, "schemas" for GraphQL, "handlers" for Go HTTP, "controllers" for Rails).
9. **Monorepo handling** — if the project is a monorepo, first map all packages/services, then analyze each as a sub-project with its own mini-overview.
