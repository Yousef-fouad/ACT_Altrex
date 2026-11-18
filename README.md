# Accounting workflows through AI-assisted vibe coding

An accounting research project with Professor Julia Kokina. Recreate accounting
workflows traditionally completed in Alteryx using Python, Marimo, VS Code,
GitHub, and Claude or Codex. You already know Marimo: focus on accounting logic,
workflow design, communicating with AI, and checking results. You do not need
to write Python manually. AI generates the code; you remain responsible for
the accounting decisions and evidence that the results are correct.

No completed assignment solution is included. Your instructor demonstrates the
method with a separate example; you independently design your assigned workflow.

## 1. Create your private repository

Use the **student-template link supplied by the instructor**, not a search result
or the administrator repository. Sign in to GitHub, choose **Use this template →
Create a new repository**, select your own account as owner, name the repository
as instructed, and select **Private**. Leave **Include all branches** unchecked.
Create the repository and confirm the **Private** label beside its name.

Do not fork the template or clone the administrator repository. A repository
[created from a template starts with a new history](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).
If the link has no template button or contains a completed assignment, stop and
contact the instructor. A private link alone does not grant access.

## 2. Open your repository in VS Code

Install [VS Code](https://code.visualstudio.com/), [Git](https://git-scm.com/downloads),
and [uv](https://docs.astral.sh/uv/getting-started/installation/) if needed. Use
the official installers or your institution's approved installation method.
Restart VS Code after installing command-line tools.

In VS Code, open the Command Palette (**Ctrl+Shift+P**, or **Cmd+Shift+P** on Mac),
choose **Git: Clone**, and paste the URL of **your new private repository**.
Choose a local folder, sign in to GitHub if prompted, and open the cloned folder.
Trust it only if it is the repository you just created.

## 3. Set up Python with uv

Open **Terminal → New Terminal** in VS Code. The terminal should be in the folder
containing [pyproject.toml](./pyproject.toml). Run:

```text
uv sync --locked
```

uv creates a local `.venv` environment and installs the versions recorded in
[uv.lock](./uv.lock). The project selects Python 3.14; uv can download it if it
is not installed. No manual environment activation is needed for `uv run`.
If VS Code asks for an interpreter, choose the Python interpreter in `.venv`.

If installation fails, share the error with your assistant or instructor.
Do not delete the lockfile, run a package upgrade, or switch to pip/conda as a
workaround. [uv's project guide](https://docs.astral.sh/uv/guides/projects/)
explains the environment files. Only Marimo, pandas, and openpyxl are direct
project dependencies; other installed packages support them.

## 4. Open Claude or Codex

Use the course-approved [Claude Code VS Code extension](https://code.claude.com/docs/en/vs-code)
or [Codex VS Code extension](https://developers.openai.com/codex/ide/), and sign in
using your approved account. Work with your cloned repository open. Account
access depends on your institution and chosen service; no API key is included
or required by the accounting notebook itself.

Tell Claude to follow [CLAUDE.md](./CLAUDE.md), or Codex to follow
[AGENTS.md](./AGENTS.md). These files contain equivalent course instructions.
The assistant may request tool permissions; review them. You can authorize it
to generate, execute, debug, and validate the full workflow without approving
each individual transformation. GitHub publishing and access changes remain
separate actions that need your instruction.

## 5. Design and communicate your workflow

Read [assignment.md](./assignment.md) and inspect the original workbooks described
in [starter_data/README.md](./starter_data/README.md). Explain the accounting
problem and your intended approach in your own words before asking for a solution.

You may describe your workflow in text or upload a drawing through the assistant's
attachment control when available. You can also save a drawing under `workflow/`
and ask the assistant to inspect it. Include clear labels and arrows. If image
inspection is unavailable, describe the drawing in text. Explain your intended
matching rules, calculations, outputs, and how you will check them. Ask AI to
flag unclear accounting choices rather than silently decide them.

Use a prompt such as this, replacing the brackets with **your own plan**:

> Follow the course AI instructions. My intended workflow is [my description],
> or see [my attached drawing]. Interpret my plan and flag material ambiguities.
> Generate an executable Marimo notebook with labeled stages, intermediate
> interactive tables, Alteryx equivalents, a workflow diagram, actual cell
> dependencies, and financial checks. Execute, debug, and validate it. Do not
> change source files or export a report until I intentionally request export.

Save your plan and important revisions in `workflow.md`. Keep the original drawing
if you used one. There is no single required prompt; clear accounting requirements
and thoughtful validation matter more than programming vocabulary.

## 6. Generate and open your Marimo notebook

Ask your assistant to save the notebook as `notebooks/assignment_1.py`. That file
does not exist until you generate it from your own plan. Then open it:

```text
uv run --locked marimo edit notebooks/assignment_1.py
```

Use the local browser URL printed in the terminal. Keep the terminal running;
press **Ctrl+C** there when finished. Python code remains available in the editor
for inspection, but you may request changes in plain English instead of editing
code manually.

The notebook should show a visual workflow diagram and use Marimo's real cell
dependencies. Open Marimo's **dependency graph** in its sidebar/developer tools
to see which cells actually depend on others; ask AI to explain any mismatch
with your drawing. A diagram alone does not verify execution order.

## 7. Review and validate the accounting results

Inspect the interactive tables at every logical stage. Check record counts,
missing values, duplicate keys, matching exceptions, and totals. Ask why rows
changed and verify examples against the original files. Compare source totals
with intermediate data and both final reports, including country-level totals.
Do not treat a polished table or an AI statement as evidence of accuracy.

Keep full source precision unless you have an agreed accounting rounding rule.
Two-decimal display does not require rounding every stored amount. Document
currency/units, assumptions, rounding, tolerances, and unresolved exceptions in
`validation.md`. Compare with original Alteryx output if the instructor supplies
it; otherwise say that comparison was unavailable.

Ask AI to run these checks and explain actual results:

```text
uv run --locked marimo check notebooks/assignment_1.py
uv run --locked python notebooks/assignment_1.py
```

Running the notebook as a script must not write an Excel report automatically.
Critical validation failures must block export. Once checks pass and you review
the reports, use the notebook's intentional export action. Export a new draft
under `outputs/`; do not automatically overwrite existing reports. Reopen the
workbook and confirm its worksheets, columns, counts, and financial totals.
Then deliberately save or copy your reviewed workbook to
`submission/assignment_1.xlsx`. Only that final Excel filename is tracked for
submission; draft reports under `outputs/` remain ignored.

## 8. Grant reviewer access and submit

Keep your repository **Private**. On GitHub, open **Settings → Collaborators**
(or **Collaborators and teams**, depending on ownership), choose **Add people**,
and invite the professor and research assistant using the exact GitHub usernames
provided through the course. Ask them to accept. Confirm both invitations are
accepted; pending invitations do not provide reviewer access. Never invite
classmates or a class-wide team. If your repository is organization-owned, ask
the instructor to check inherited access as well.

Prepare these files:

- `notebooks/assignment_1.py`: your working, validated Marimo notebook.
- `workflow.md` and your drawing under `workflow/`, if used: your intended
  workflow and meaningful revisions.
- `validation.md`: actual checks, results, exceptions, and accounting policies.
- `submission/assignment_1.xlsx`: the final workbook with the two required sheets.
- `reflection.md`: your own short reflection on communicating with AI, revisions,
  errors you caught, and what you learned. Do not ask AI to invent your experience.

Save your work. In VS Code **Source Control**, inspect changed files and stage
the deliverables. Do not stage `.venv`, credentials, caches, or draft reports.
Commit with a clear message, then choose **Push** or **Sync Changes** to send it
to **your private repository**, not the template. If you ask AI to do this,
explicitly instruct it to commit and push after you review the files.

Finally, open your repository on GitHub and confirm all deliverables are visible,
download the final workbook to verify it, and submit the repository URL plus
the final commit identifier through the course's submission channel. The final
Excel workbook is submitted in GitHub alongside the notebook, not left only on
your computer. Confirm the professor and research assistant can open the URL.
