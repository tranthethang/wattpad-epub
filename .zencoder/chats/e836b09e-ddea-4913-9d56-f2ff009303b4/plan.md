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

- **easy**: Straightforward implementation, trivial bug fix or feature
- **medium**: Moderate complexity, some edge cases or caveats to consider
- **hard**: Complex logic, many caveats, architectural considerations, or high-risk changes

Create a technical specification for the task that is appropriate for the complexity level:

- Review the existing codebase architecture and identify reusable components.
- Define the implementation approach based on established patterns in the project.
- Identify all source code files that will be created or modified.
- Define any necessary data model, API, or interface changes.
- Describe verification steps using the project's test and lint commands.

Save the output to `/Users/thangtran/Documents/GitHub/wattpad-epub/.zencoder/chats/e836b09e-ddea-4913-9d56-f2ff009303b4/spec.md`.

---

### [x] Step: Implementation

Implement the task according to the technical specification and general engineering best practices.

1. [x] Create reproduction script for line spacing issue
2. [x] Analyze reproduction results
3. [x] Modify `process_text_for_line_breaks` to remove sentence splitting
4. [x] Update `EPUB_CSS` to remove redundant `pre-wrap` and add paragraph styles
5. [x] Verify the fix with the reproduction script
6. [x] Write a report to `/Users/thangtran/Documents/GitHub/wattpad-epub/.zencoder/chats/e836b09e-ddea-4913-9d56-f2ff009303b4/report.md` describing:
   - What was implemented
   - How the solution was tested
   - The biggest issues or challenges encountered
