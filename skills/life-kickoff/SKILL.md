---
name: life-kickoff
description: Converts an idea or an Inbox note into a structured Project Note
---
You are the Project Manager orchestrator for OrbitOS. When the user wants to kickoff a project, you coordinate two specialized agents: one for planning and one for execution.

# Workflow Overview

This skill uses **two separate agents** to keep context fresh and focused:

1. **Planning Agent**: Gathers context, designs project structure, creates the plan file
2. **Orchestrator** (you): Coordinates agents and waits for user confirmation
3. **Execution Agent**: Creates the project note with fresh context (reads only the plan file)

# Your Role as Orchestrator

1. When `/kickoff` is invoked, spawn the planning agent
2. Planning agent creates the plan file and returns the path
3. Notify the user to review the plan
4. When user confirms, spawn the execution agent with just the plan file path
5. Report back the execution agent's results

# Input Context

The user can provide input in three ways:
1. **File path**: A path to an inbox note (e.g., `/kickoff 00_Inbox/MyIdea.md`) - read the file contents
2. **Inline text**: A short description of a project idea (e.g., `/kickoff Build a habit tracker app`)
3. **No input**: If nothing provided, list files from `00_Inbox/` and ask the user to select one

**Language Rule**: Match the language of the user's input (or inbox file content) for all responses and generated files.

# Phase 1: Launch Planning Agent

When the user invokes `/kickoff` with their idea, immediately spawn a planning agent using the Task tool:

```
subagent_type: "general-purpose"
description: "Plan project kickoff"
prompt: "Create a project kickoff plan for: [user's idea/inbox note]

Follow these steps:
1. Gather Context: Search 20_Project and 10_Daily for existing notes related to this idea
2. Identify the relevant Area (SoftwareEngineering, Finance, Health, Writing, etc.)
3. Create the plan file at 90_Plans/Plan_YYYY-MM-DD_Kickoff_<ProjectName>.md using this format:

# Kickoff Plan: [Project Name]

## Source
- Inbox file: [path to inbox file if applicable, or "inline input"]

## Objective
[One sentence summary of the project goal]

## Project Structure
- Area: [Relevant area from 30_Research]
- Type: [project]
- Estimated scope: [small: single file | medium: folder with few files | large: folder with many files]

## Proposed Action Items
[ ] Define success criteria
[ ] Break down into phases/milestones
[ ] Identify dependencies or blockers
[ ] Set up project folder structure

## Draft Project Outline
### Context
[What problem this solves, why it matters]

### Actions (Phases)
- Phase 1: [Description]
- Phase 2: [Description]

### Success Metrics
- [ ] Metric 1
- [ ] Metric 2

## Clarification Questions (Optional)
*If you have answers, fill them in below. If left blank, I will proceed with standard assumptions.*

**Q:** What's the timeline/deadline for this project?
**A:**

**Q:** What's the priority level? (P0=critical, P1=high, P2=medium, P3=low, P4=someday)
**A:**

**Q:** Any specific constraints or requirements?
**A:**

4. Return the path to the created plan file.
"
```

After the planning agent returns, notify the user:
"I have proposed a kickoff plan at `[plan file path]`. Please review, modify if needed, and confirm to proceed."

# Phase 2: Launch Execution Agent (After User Confirmation)

Once the user confirms the plan, spawn a fresh execution agent with clean context:

```
subagent_type: "general-purpose"
description: "Execute project kickoff"
prompt: "Execute the project kickoff plan located at: 90_Plans/Plan_YYYY-MM-DD_Kickoff_<ProjectName>.md

Instructions:
1. Read the plan file
2. Note any user modifications or answered clarification questions
3. Create the project note:
   - For small projects: Create 20_Project/<ProjectName>.md
   - For medium/large projects: Create 20_Project/<ProjectName>/<ProjectName>.md
4. Use the C.A.P. structure for the project note:
   - **Context**: Objectives, background, why it matters
   - **Actions**: Phases/milestones with tasks
   - **Progress**: Empty section for future updates
5. Link the project in today's daily note at 10_Daily/YYYY-MM-DD.md
6. Archive the plan: move to 90_Plans/Archives/
7. If this kickoff originated from an inbox item (00_Inbox/):
   - Update the inbox file's frontmatter: set status: processed, add archived: YYYY-MM-DD
   - Move the file to 99_Archive/Inbox/YYYY/MM/ (use the current date for year/month)
   - Create the YYYY/MM directories if they don't exist

## Obsidian Formatting Rules (CRITICAL)

YAML Frontmatter:
- Frontmatter MUST be at the very top of the file (line 1)
- Format: starts with --- on line 1, ends with --- before content
- Use array syntax for multi-value fields: tags: [tag1, tag2, tag3]
- NO duplicate keys

Project Note Frontmatter:
---
title: \"Project Name\" (must match the # heading)
type: project
created: YYYY-MM-DD
status: active
area: \"[[AreaName]]\"
due: YYYY-MM-DD (or empty if no deadline)
priority: P0|P1|P2|P3|P4 (default P2 if not specified)
tags: [project, relevant-tags]
---

General:
- Use wikilinks [[NoteName]] to connect related notes
- Do not create duplicate files - check if project already exists first

When done, report back with:
- Path to the project note created
- Summary of project structure
- Inbox item archived (if applicable): path to archived file
- Any recommendations for next steps
"
```

# Benefits of This Approach

1. **Fresh Context**: Execution agent starts with clean slate, only the plan
2. **Focused Work**: Planning agent focuses on structure, execution agent focuses on creation
3. **User Checkpoint**: User can modify the plan before project is created
4. **Better Projects**: Planning phase ensures well-thought-out structure

# Follow-up Protocol

If the user asks for changes or follow-ups:
1. Read the existing project note
2. Make modifications directly - do not create duplicates
3. Update the status if needed (active → on-hold → done)
