# Ender Turing Full-Stack Developer Test Task

This assignment is for a developer role at Ender Turing.

Add role-aware access control to the existing
[Full-Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template/tree/master).

The stack is FastAPI, SQLModel, PostgreSQL, React and TypeScript.

## Timebox

Aim for about **one hour**. Submit the best coherent solution you can within that
time and state how long you actually spent.

AI coding tools are allowed. You remain responsible for every submitted change.

Prioritize working, understandable code. There is no bonus for extensive
documentation, diagrams, agent configuration, generated reports or a large number
of tests.

## Product requirements

Introduce three access levels:

- **Admin** can manage users and their access.
- **Manager** can view users and metrics, but cannot change user access.
- **Member** can access and update their own profile.

The metrics page may be a simple stub. Existing application features should keep
working unless a change is necessary for the new access model.

Authorization must be enforced by the backend. The frontend should reflect the
same access rules and handle direct navigation to unauthorized pages sensibly.

For behavior that is not specified, make reasonable assumptions and implement
them consistently.

## Existing production context

Treat the template as an already deployed application, not a new project:

- The database contains existing users created with the current `is_superuser`
  model.
- Existing data must survive the migration without unintended privilege changes.
- Access or active-status changes must affect users who already have a session.
- Assume migrations run against a populated database.

You decide how roles or permissions are represented, how compatibility is handled,
where authorization checks live, and how the backend and frontend communicate
access information.

## Expected implementation

- A database migration for any schema changes.
- Backend and frontend behavior for all three access levels.
- Focused automated tests for the security-critical behavior you consider most
  important.
- A minimal way for the reviewer to exercise all three access levels locally.
- Existing project setup and test commands should continue to work. If your changes
  require different commands, update the relevant instructions.

Keep the change focused. Unrelated refactoring, infrastructure work and visual
polish are outside the task.

## Submission

Provide only:

1. A GitHub repository or pull request containing the working implementation and
   its commit history.
2. The commands needed to run the solution and its tests, if they differ from the
   original template.
3. The **complete raw export** of every AI coding conversation used for the task,
   committed under `ai-conversations/`.

The AI export must contain the original prompts and responses. A summary,
retelling, selected excerpts or generated description of the conversation is not
a replacement for the raw export. Remove secrets if necessary and mark any
redactions clearly.

The code is the primary deliverable. We will review correctness, security,
maintainability, consistency, migration safety, scope control, and how the AI tool
was directed and validated.

Be prepared to explain the implementation and make a small change to an access
rule during a follow-up conversation.
