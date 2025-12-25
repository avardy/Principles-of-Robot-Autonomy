# Principles of Robot Autonomy – Copilot Instructions

## Layout & Ownership
- Authoritative content lives under `tex/source/*.tex`; edit these files when updating prose or equations.
- `tex/combined.tex` stitches every chapter/appendix (in pedagogical order) and defines the parts; keep this file updated when chapters are added, renamed, or re-ordered.
- `tex/chapterXX_*.tex` are slim wrappers that compile single-chapter PDFs by `\input`-ing the shared source; mirror combined-chapter names but avoid duplicating content there.
- Generated artifacts live in `chapters/*.pdf` and `PrinciplesofRobotAutonomy.pdf`; never hand-edit these outputs.

## Build Workflows
- From the repo root run `cd tex && latexmk -pdf combined.tex` to build the full book; `latexmk` auto-invokes `biber` because the project uses `biblatex`.
- For targeted chapter refreshes run `cd tex && latexmk -pdf chapter05_SearchBasedMotionPlanning.tex` (replace filename as needed).
- If bibliography changes, or citations appear unresolved, run `cd tex && biber combined` once between repeated `latexmk` passes.
- Clean auxiliary files with `cd tex && latexmk -c` before committing to keep the repo lean.

## Writing Conventions
- Each chapter starts with `\notessection{...}` followed by `\subsection`/`\paragraph`; `\subsubsection` is aliased to `\subsection` in `tex/preamble.tex`, so keep the outline shallow.
- Use the macros from `tex/preamble.tex` (`\python`, `\pythonexternal`, `\gencode`, theorem environments, bold-symbol shortcuts) instead of redefining similar constructs per chapter.
- Figures should be stored under `tex/figs/chXX_figs/` and referenced via `\includegraphics{tex/figs/...}` so paths work for both combined and single-chapter builds.
- Prefer vector/PDF figures when possible; if you need to regenerate data-driven graphics, check for MATLAB helpers (e.g., `tex/figs/ch18_figs/carKFfusion.m`) and keep scripts alongside the exported assets.

## Citations & Index
- Bibliography entries live in `tex/references.bib`; cite with `\cite{key}` (redefined to tufte-style sidenotes) and run `biber` after adding entries.
- The preamble already enables `\index{}`; add index entries inline when introducing major concepts so the compiled index stays useful.

## When Editing Structure
- Adding a new chapter requires (1) creating `tex/source/chXX.tex`, (2) adding a matching wrapper `tex/chapterXX_*.tex`, and (3) inserting the chapter in the right `\part` block inside `tex/combined.tex`.
- Keep `\part` boundaries aligned with course pillars (Motion Planning & Control, Perception, Localization, Decision Making, Software, Advanced Topics, Appendices) so the Table of Contents remains coherent.

## Review Checklist
- After changes, build at least the affected chapter to catch TeX regressions.
- Verify every new figure path resolves under both combined and chapter-only builds.
- Ensure any new macros or packages are centralized in `tex/preamble.tex` to prevent drift across chapter wrappers.
