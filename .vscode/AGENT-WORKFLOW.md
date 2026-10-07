# Pixel Agent Workflow

## Goal

Use King Agents as a visible multi-agent office so you can see what each agent is doing. The agents must not act independently.

## Execution Rule

1. You provide one task at a time.
2. The office shows the role, current action, and relevant files.
3. The agent may inspect the workspace and explain its plan.
4. You must approve every file change, terminal command, dependency installation, and test run.
5. After approval, the agent may execute only the approved action.
6. If you do not approve, the agent stays in observation mode and does not modify the workspace.

## Approved Workflow

1. **Architect** — inspect the request and produce a short plan.
2. **Researcher** — inspect existing code and dependencies, then report facts.
3. **Coder** — present the exact files and changes before editing.
4. **QA Reviewer** — present the tests and verification command before running them.
5. **Technical Writer** — present documentation updates before editing README or docs.

## Agent Visibility

Use these commands from the Command Palette:

- `King Agents: Start New Task (新任务)` — start one approved task.
- `King Agents: Open Office (打开办公室)` — open the pixel office and watch the agents.
- `King Agents: Cancel Session (取消任务)` — stop the current session.
- `King Agents: Show Stats (统计)` — inspect session history.

## Safety Rules

- Never let an agent run a command without your approval.
- Never let an agent modify files without showing the proposed change.
- Never let multiple agents work in parallel without your explicit approval.
- Treat every agent output as a proposal, not an executed fact.
- If the agent asks to install dependencies or run tests, ask for approval first.
