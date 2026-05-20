# 🚀 Modular AI SDLC Agent Skills

A standardized, professional Software Development Life Cycle (SDLC) pipeline built for AI coding agents (like Claude Code, Cursor, Windsurf, or Gemini CLI). 

This repository provides a set of highly optimized, interoperable "skills" that enforce strict architectural boundaries, automated quality assurance, regression testing, and safe conventional branch-specific Git commits.

---

## 📖 For Non-Technical Users: What is this?
Imagine you have an expert software engineer assistant (an AI Agent). If you don't give it rules, it might write code in messy ways, forget to test, or make commits directly to your live production branch by accident. 

These **SDLC Skills** act as a **guardrail manual** for your AI assistant. It forces the AI to:
1. **Understand your project context** and rules first before writing a single line of code.
2. **Make a clear blueprint plan** and show it to you.
3. **Write automated tests and manual testing steps** so you (even if you don't know how to code) can test it yourself with mock data.
4. **Review its own code** for bugs.
5. **Commit the changes safely** to a private draft branch rather than breaking your main code.

---

## ⚙️ How to Install
You can easily add these skills globally or directly to any of your active project repositories.

1. **Download & Zip:** Download this repository as a `.zip` file.
2. **Extract:** Extract the folders inside `skills/` directly to your IDE configuration folders at your project root:

| Agent / IDE | Folder Path to Extract Into |
|---|---|
| **Claude Code** | `.claude/skills/` |
| **Cursor IDE** | `.cursor/skills/` |
| **Windsurf IDE** | `.windsurf/skills/` |
| **Gemini CLI** | `.gemini/skills/` |

For example, your folder structure in a Cursor project will look like:
```text
your-project-root/
└── .cursor/
    └── skills/
        ├── context-init/
        ├── project-division/
        ├── planning/
        ├── qa-tester/
        ├── code-review/
        └── code-commit/
```
Once unzipped, the AI Agent will automatically discover these skills as active commands (e.g., `/planning`, `/qa`, `/git-commit`).

---

## 🛠️ The 7 Core Skills

### 1. `context-init`
* **Command:** `/context-init`
* **Description:** Initializes project-wide metadata by scanning the codebase or parsing a PRD. Generates `.sdlc/CONTEXT.md` and `.sdlc/rules/code-craft.md` (which documents coding style and repository architecture rules). **Must be run once before any other skill.**

### 2. `project-division` (Optional)
* **Command:** `/project-division`
* **Description:** Useful for starting a brand new project from scratch. It breaks the PRD down into feature-complete development chunks (divisions) with specific scope, acceptance criteria, and out-of-scope boundaries.

### 3. `planning`
* **Command:** `/planning <feature or division>`
* **Description:** Takes your feature assignment and drafts a comprehensive step-by-step implementation blueprint. It creates micro-task checklists and links them directly to code implementation templates matching your specific architecture standards.

### 4. `qa-tester`
* **Command:** `/qa <feature or division>`
* **Description:** Automatically discovers what was supposed to be built, explores the codebase, runs existing tests, writes missing test coverage, performs regression tests on previous features, and generates a QA report with a step-by-step manual testing guide with mock data.

### 5. `code-review` (Optional)
* **Command:** `/code-review <feature>`
* **Description:** Scans the modified files and matches them against the dynamic code-craft rules. Verifies architectural layer compliance (e.g., ensuring routers don't make direct database queries) and highlights potential regressions or code smells.

### 6. `git-commit`
* **Command:** `/git-commit <feature>`
* **Description:** Checks branch safety, registers changes, builds a beautiful commit message matching **Conventional Commits** standards using your task plan, and safely commits your changes. **Explicitly blocks committing directly to protected branches (main, staging, master, develop).**

### 7. `architecture-diagram`
* **Command:** `/architecture-diagram`
* **Description:** Renders a gorgeous, self-contained HTML visual architecture flow diagram of your project modules and layers for easy system documentation.

---

## 📂 The `.sdlc` Folder Structure
All skills output their standardized plans, reports, and contexts to a single, localized folder at your repository root:

```text
.sdlc/
├── CONTEXT.md                      # Injects core tech stack and repository structure
├── rules/
│   └── code-craft.md               # Your customized coding rules and design patterns
├── planning/
│   ├── project_divisions.md        # Whole-project breakdown (if divided)
│   └── <feature_name>.md           # Feature micro-tasks and phases
├── implementation/
│   └── <feature_name>/             # Detail folder containing phase-by-phase blueprints
│       ├── <feature>_phase_1.md
│       ├── <feature>_phase_2.md
│       └── ...
├── qa/
│   └── <feature>_qa_report.md      # Auto-generated QA reports & manual testing guides
└── changelogs/
    └── changelog.md                # A single consolidated history of all completed work
```

---

## 🔄 Step-by-Step Manual Workflows

### Flow A: Developing a Single Feature (Assigned Task)
If you have an existing codebase and you are assigned a new feature, follow this manual step-by-step pipeline with your agent:

#### Step 1: Initialize Context (One-time)
Type this command in your AI chat window:
```text
/context-init
```
*The agent will scan your codebase and create `.sdlc/CONTEXT.md` and `.sdlc/rules/code-craft.md`.*

#### Step 2: Plan the Feature
Type this command:
```text
/planning "Create a User Login Page"
```
*The agent will check the context, ask any clarifying questions, and write `.sdlc/planning/user_login.md` and step-by-step phase files.*

#### Step 3: Implement Code
Follow the implementation blueprint generated by the planning skill phase-by-phase:
```text
Implement Phase 1 from .sdlc/planning/user_login.md
```
*(Have the agent execute the code and run local tests as outlined in the phase implementation files).*

#### Step 4: Run Quality Assurance (QA)
When implementation is finished, type:
```text
/qa "User Login Page"
```
*The agent will run a complete QA sweep, generate test files, do a regression check, and create `.sdlc/qa/user_login_qa_report.md` complete with **mock data testing steps**.*

#### Step 5: Review (Optional)
If you want an architectural double-check, type:
```text
/code-review "User Login Page"
```

#### Step 6: Safe Git Commit
When QA passes, type:
```text
/git-commit "User Login Page"
```
*The agent will verify that you are on a feature branch (refusing to commit on main/staging), stage the correct files safely, update your project changelog, and commit with a clean message.*

---

### Flow B: Whole Project Breakdown (From Scratch)
If you are planning a brand new application from a raw PRD document:
1. Initialize context: `/context-init`
2. Break the project down into divisions: `/project-division`
3. Implement division by division using Flow A (Step 2 through Step 6).
