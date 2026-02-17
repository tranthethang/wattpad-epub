# Spec and build

## Agent Instructions

Ask the user questions when anything is unclear or needs their input. This includes:

- Ambiguous or incomplete requirements
- Technical decisions that affect architecture or user experience
- Trade-offs that require business context

Do not make assumptions on important decisions — get clarification first.

---

## Workflow Steps

### [x] Step: Technical Specification

Assess the task's difficulty, as underestimating it leads to poor outcomes.

- easy: Straightforward implementation, trivial bug fix or feature
- medium: Moderate complexity, some edge cases or caveats to consider
- hard: Complex logic, many caveats, architectural considerations, or high-risk changes

Create a technical specification for the task that is appropriate for the complexity level:

- Review the existing codebase architecture and identify reusable components.
- Define the implementation approach based on established patterns in the project.
- Identify all source code files that will be created or modified.
- Define any necessary data model, API, or interface changes.
- Describe verification steps using the project's test and lint commands.

Save the output to `/Users/thangtran/Documents/GitHub/wattpad-epub/.zencoder/chats/c1ccae1e-75f5-4044-b5c3-72fc3b00c86e/spec.md` with:

- Technical context (language, dependencies)
- Implementation approach
- Source code structure changes
- Data model / API / interface changes
- Verification approach

If the task is complex enough, create a detailed implementation plan based on `/Users/thangtran/Documents/GitHub/wattpad-epub/.zencoder/chats/c1ccae1e-75f5-4044-b5c3-72fc3b00c86e/spec.md`:

- Break down the work into concrete tasks (incrementable, testable milestones)
- Each task should reference relevant contracts and include verification steps
- Replace the Implementation step below with the planned tasks

Rule of thumb for step size: each step should represent a coherent unit of work (e.g., implement a component, add an API endpoint, write tests for a module). Avoid steps that are too granular (single function).

Save to `/Users/thangtran/Documents/GitHub/wattpad-epub/.zencoder/chats/c1ccae1e-75f5-4044-b5c3-72fc3b00c86e/plan.md`. If the feature is trivial and doesn't warrant this breakdown, keep the Implementation step below as is.

---

### [x] Step: Implementation

Implement the task according to the technical specification and general engineering best practices.

1. [x] Filter URLs in `src/main.py`'s `get_urls` command to only include those starting with `http://` or `https://`.
2. [x] Run a manual test to verify the fix.
3. [x] After completion, write a report to `/Users/thangtran/Documents/GitHub/wattpad-epub/.zencoder/chats/c1ccae1e-75f5-4044-b5c3-72fc3b00c86e/report.md`.
