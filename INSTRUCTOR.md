# Administrator release checklist

This is the administrator repository for Professor Julia Kokina's research
project. Do not share its URL as the student template while its history contains
solutions. Removing a tracked file does not remove old commits.

## Instructor reference

The original notebook has a byte-for-byte verified local backup at
`.git/instructor-reference/assignment_1.original.py`. The reviewed version and
accounting audit are in the same directory. This directory is not tracked,
cloned, or included in template generation. It is local-only storage, **not a
durable backup or a separate access-control boundary**. Copy it to institutionally
approved restricted instructor storage before replacing or deleting this checkout.
Do not give students this checkout, its Git directory, or its local caches.

## Publish a clean template only after approval

1. Review the changed student materials. Prepare an allowlisted, history-free
   snapshot in a new directory (PowerShell, from this administrator repository):

   ```powershell
   ./scripts/prepare-student-template.ps1 -Destination ./student-release
   ```

   If Windows blocks local scripts, use a process-only invocation (no permanent
   execution-policy change):

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/prepare-student-template.ps1 -Destination student-release
   ```

   The script refuses existing destinations. Use another `student-release-*`
   name for later releases. It copies original datasets unchanged, never completed notebooks,
   instructor notes, generated reports, session caches, or Git history.
2. Test `uv sync --locked` in that directory. Verify only the reviewed files are
   present, then run a volunteer student trial using their own plan and drawing.
3. With repository-owner approval, publish **only the 14 allowlisted files** as the first
   commit of a new student-template repository. Do not fork, clone-and-push,
   copy `.git`, or import this administrator repository's history. Set the new
   repository as a GitHub template. Do not make this administrator repository
   public as a shortcut. Existing exposure cannot be undone by a clean release.
   Do not upload the `.venv` created during testing; it is ignored by Git.
4. Give students the new template URL. They choose **Use this template**, a
   **private** repository under their own account, and the default branch only.
5. Supply the professor's and research assistant's exact GitHub usernames through
   the course channel. They must accept each student's collaborator invitation.
   Test that each reviewer can open every submission and a second student cannot.
   The actual GitHub settings and access checks require authenticated testing;
   local files cannot enforce them.

GitHub documents that [templates start with a single commit, unlike forks](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).
That protects the new repository's history, not a readable administrator source.
A private template still requires students to have read access, so never use an
instructor repository with answer history as that private template.

## Submission access

Personal private repositories are the simplest default. Invite only the two
reviewers, never classmates or a class-wide team. If using an organization,
check base permissions, inherited teams, owners, and repository policies first;
private visibility alone does not remove inherited access. Student owners can
change their own sharing settings, so confidentiality also requires course rules
and verification. Never share account credentials or tokens.

The submission convention is documented in the student README: final Excel in
`submission/assignment_1.xlsx`, generated notebook, workflow plan/drawing,
validation evidence, and reflection. Draft outputs remain ignored.

## Outstanding release decisions

- Approve the separate student-template repository name and visibility and provide
  its shared URL. No remote settings are changed by this preparation.
- Provide reviewer usernames and verify accepted invitations with test accounts.
- Supply the original Alteryx output and any original instructions beyond
  `assignment.md` to establish external parity and the intended rounding policy.
- Confirm currency/units and whether rounding is display-only or required at a
  defined accounting stage. The reviewed instructor reference preserves source
  precision; no currency conversion is invented.
- Securely back up the local-only instructor reference outside this checkout.
