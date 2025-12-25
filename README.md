# Principles of Robot Autonomy

This repository contains the LaTeX source for the "Principles of Robot Autonomy" course notes as well as curated Beamer slide decks for each chapter.

## Repository Layout
- `book/source/`: canonical chapter content. Edit these files to update prose, equations, or figures.
- `book/`: TeX wrappers, combined book build (`combined.tex`), bibliography, and figures (`book/figs/chXX_figs`).
- `chapters/`: generated chapter PDFs (do not edit manually).
- `slides/`: curated Beamer decks (e.g., `ch01.tex`), `common_preamble.tex`, and any reusable templates/guides.
- `ORIGINAL_README.md`: short note from the upstream release, retained for reference.

## Slide Conversion Workflow
1. **Seed a deck**
   - Copy an existing curated deck such as `ch01.tex` and update the metadata/title slide.
   - All decks should `\input{common_preamble.tex}` to pick up shared theme/`
     usepackage` settings.
2. **Curate slides manually**
   - Group related paragraphs into balanced frames (aim for 2–4 bullets per slide).
   - Keep equations in math mode; do not flatten LaTeX macros.
   - Insert figures where they add clarity; ensure paths are valid from `slides/` (e.g., `../tex/figs/chXX_figs/...`).
3. **Preserve original text**
   - After each frame, add a commented block containing the exact source snippet. This maintains traceability back to `tex/source/chXX.tex`.
4. **Review & build**
   ```bash
   cd slides
   latexmk -pdf ch01.tex
   ```
   Fix any Beamer warnings (imbalanced `$`, missing figures) before committing.
5. **Harden shared macros & frames**
   - When a build fails because a command such as `\bxi` is undefined, search the chapter source to confirm the definition and add a matching `\newcommand` (or import) to [slides/common_preamble.tex](slides/common_preamble.tex) so every deck shares it.
   - After each edit pass, scan the deck for frames that include verbatim-style content (code listings, `minted`, `verbatim`, `\includegraphics`, etc.) and ensure those frames opt into `\begin{frame}[fragile]` to prevent compilation errors.

## Slide Authoring Preferences
- **Scope**: Summaries operate at the subsection/paragraph level; avoid one-sentence slides unless the content is a definition or equation.
- **Length**: Err on the side of slightly longer summaries so each frame captures enough context to stand alone before referencing the comments.
- **Math**: Always wrap operators and symbols in `$...$` to keep LaTeX semantics intact.
- **Reminders**: Whenever a slide relies on technical mathematical concepts that students may have forgotten (e.g., null space, gradient), insert a short reminder frame beforehand. Wrap the reminder bullets inside a boxed element with a light gray background (e.g., a `block` environment with `bg=gray!10`) so the recap visually stands apart. Focus on the concept itself—not the surrounding slide context—and always close with a single concrete example that illustrates the refreshed idea.
- **Balance**: Combine short paragraphs so each frame covers a coherent idea, usually 2–3 bullets plus optional equations/figures; lists animate by default (override with `\begin{itemize}[<*>]` etc. if you need static bullets).
- **Animation**: Every frame element should either sit inside `itemize`/`enumerate` or use `\paragraph{}` so the shared preamble can manage overlays consistently.
- **Equations & Figures**: Precede every displayed equation or `\includegraphics` block with an explicit `\pause` (or equivalent overlay command) so math and visuals appear after the narrative bullets instead of skipping ahead in the animation order.
- **Figures**: Reference originals under `tex/figs/chXX_figs` and keep paths valid when compiling from `slides/` (use `../tex/figs/...`). Every figure or illustration mentioned in the source should also make it into the slides—replicate or adapt the visual instead of dropping it.
- **Slide-Only Visuals**: Place any new artwork created specifically for slides (and not present in the chapters) under `slides/figs/` with a chapter-specific subfolder to keep assets organized.
- **Figure Assets**: Store slide-ready figures alongside the existing assets under `tex/figs/chXX_figs/` (or a chapter-specific subfolder) so both the combined notes and the slide decks can reuse the same files. If you redraw or simplify a figure, keep the underlying data or scripts (MATLAB, Python, etc.) in that subfolder for reproducibility.
- **Traceability**: Comment the raw source text beneath the slide (`% --- Original text start ---`) and include the full paragraph(s) without truncation so later edits have the complete reference.

For questions or suggestions, open an issue or reach out to the maintainers listed in the course materials.

## Slide Build Automation
- A dedicated [slides/Makefile](slides/Makefile) wraps `latexmk` so you can build from the repo root with `make -C slides`.
- Build everything (default goal): `make -C slides`.
- Build a subset by passing `SLIDES`: `make -C slides SLIDES="ch03 ap01"` (extensions are optional).
- Enable handout mode by toggling the `HANDOUT` flag, which injects `\documentclass[handout]{beamer}` via `\PassOptionsToClass`: `make -C slides HANDOUT=1 SLIDES=ch03`. Handout builds also emit a `*_quad.pdf` companion (2x2 grid suitable for printing) using `pdfjam`.
- Clean only the selected decks with `make -C slides clean SLIDES=ch03`; remove every auxiliary/PDF artifact with `make -C slides clean-all`.
