# Principles of Robot Autonomy – Copilot Instructions

These notes focus exclusively on the curated slide decks under `slides/`. The main workflow, preferences, and book-building steps now live in [README.md](../README.md); lean on that file for authoritative guidance.

## Slide Layout & Ownership
- Deck sources live in `slides/` (e.g., `ch10.tex`, `ap01.tex`) plus the shared `common_preamble.tex`.
- Figures are shared with the textbook; reference them via `../book/figs/chXX_figs/...` so a single asset works for both the book and slides.
- Generated PDFs (`chXX_present.pdf`, `chXX.pdf`, `chXX_quad.pdf`) are disposable build products; never commit them.

## Slide Workflow (see README for details)
1. Copy an existing deck such as `ch01.tex` when starting a new chapter and update the metadata.
2. Summaries should keep LaTeX math intact, include a brief reminder block when background concepts are introduced, and preserve the original prose in `% --- Original text ---` comments.
3. Every deck must `\input{common_preamble.tex}` and use `\begin{frame}[plain]\titlepage\end{frame}` for the opening slide.
4. Build with `make -C slides SLIDES="ch10"` (presentation) and `make -C slides HANDOUT=1 SLIDES="ch10"` (handout + quad). The `compile_slides.sh` helper wraps these invocations.

## Authoring Reminders
- Keep frames balanced (2–4 bullets), gate figures/equations with `\pause`, and mark any verbatim/code-heavy frames as `[fragile]`.
- Store new slide-only art under `slides/figs/` with chapter-specific folders; include any scripts used to generate them.
- Shared macros belong in `common_preamble.tex`; avoid redefining them per deck.

## Build Hygiene
- `make -C slides clean SLIDES="ch10"` removes aux files for the selected deck; `clean-all` purges every auxiliary/PDF/quads.
- Handout builds automatically create `*_quad.pdf` using `pdfjam`; ensure `pdfjam` is installed on your system.
- If a build fails after cleaning `.nav/.snm` files, rerun `make` so latexmk can regenerate navigation metadata.
