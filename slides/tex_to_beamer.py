#!/usr/bin/env python3
"""Convert a source TeX chapter into a lightweight Beamer presentation."""
from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

SECTION_PATTERN = re.compile(r"\\(notessection|section|subsection|subsubsection|chapter)\s*\{([^}]*)\}")
CAPTION_PATTERN = re.compile(r"\\caption\s*\{([^}]*)\}")
COMMAND_PATTERN = re.compile(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?")
INLINE_MATH_PATTERN = re.compile(r"\$([^$]+)\$")
INCLUDE_PATTERN = re.compile(r"(\\includegraphics(?:\[[^\]]*\])?\{)([^{}]+)(\})")
ABBREVIATIONS = (
    "e.g.",
    "i.e.",
    "etc.",
    "Fig.",
    "Figs.",
    "Eq.",
    "Eqs.",
    "Sec.",
    "Secs.",
    "Dr.",
    "Mr.",
    "Mrs.",
    "Ms.",
    "Prof.",
    "vs.",
)
ABBREV_PLACEHOLDER = "<<DOT>>"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a TeX source file to a Beamer summary.")
    parser.add_argument("input", type=Path, help="Path to the source .tex file (e.g., tex/source/ch01.tex)")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for the generated Beamer file. Defaults to <repo_root>/slides/<stem>.tex",
    )
    return parser.parse_args()


@dataclass
class Block:
    kind: str
    lines: List[str]
    title: Optional[str] = None


def read_blocks(lines: List[str]) -> List[Block]:
    blocks: List[Block] = []
    buffer: List[str] = []

    def flush_buffer() -> None:
        nonlocal buffer
        if not buffer:
            return
        kind = "figure" if any("\\includegraphics" in ln for ln in buffer) else "text"
        blocks.append(Block(kind=kind, lines=buffer))
        buffer = []

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        match = SECTION_PATTERN.match(line.strip())
        if match:
            flush_buffer()
            role, title = match.group(1), match.group(2).strip()
            blocks.append(Block(kind=role.lower(), lines=[], title=title))
            continue
        if not line.strip():
            flush_buffer()
            continue
        if line.lstrip().startswith("%"):
            continue
        buffer.append(line)

    flush_buffer()
    return blocks


def tex_to_plain(text: str) -> str:
    text = INLINE_MATH_PATTERN.sub(r"\1", text)
    text = COMMAND_PATTERN.sub(" ", text)
    text = re.sub(r"\{[^{}]*\}", " ", text)
    text = re.sub(r"\\", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    protected = text
    for abbr in ABBREVIATIONS:
        protected = protected.replace(abbr, abbr.replace(".", ABBREV_PLACEHOLDER))
    parts = re.split(r"(?<=[.!?])\s+", protected)
    sentences: List[str] = []
    for part in parts:
        restored = part
        for abbr in ABBREVIATIONS:
            restored = restored.replace(abbr.replace(".", ABBREV_PLACEHOLDER), abbr)
        restored = restored.strip()
        if restored:
            sentences.append(restored)
    return sentences


def summarize_block(lines: List[str]) -> str:
    raw = " ".join(line.strip() for line in lines)
    cleaned = tex_to_plain(raw)
    if not cleaned:
        return "Refer to detailed notes in the comments."
    sentences = split_into_sentences(cleaned)
    if not sentences:
        return "Refer to detailed notes in the comments."
    summary = sentences[0]
    if len(summary.split()) < 12 and len(sentences) > 1:
        summary = f"{summary} {sentences[1]}"
    words = summary.split()
    if len(words) > 45:
        summary = " ".join(words[:45]) + " ..."
    return summary.strip()


SPECIAL_CHARS = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}


def escape_tex(text: str) -> str:
    result = []
    for char in text:
        result.append(SPECIAL_CHARS.get(char, char))
    return "".join(result)


def comment_block(lines: List[str]) -> List[str]:
    commented = ["% --- Original block start ---"]
    commented.extend(f"% {line}" if line else "%" for line in lines)
    commented.append("% --- Original block end ---")
    return commented


def build_header(title: str, source_name: str) -> List[str]:
    return [
        "\\documentclass{beamer}",
        "\\usetheme{Madrid}",
        "\\usecolortheme{seagull}",
        "\\usepackage{graphicx}",
        "\\usepackage{amsmath}",
        "\\usepackage{bm}",
        "\\title{" + escape_tex(title) + "}",
        "\\subtitle{Auto-generated from ``" + escape_tex(source_name) + "''}",
        "\\author{Principles of Robot Autonomy}",
        "\\date{\\today}",
        "",
        "\\begin{document}",
        "\\frame{\\titlepage}",
    ]


def figure_payload(lines: List[str], input_dir: Path, output_dir: Path) -> List[str]:
    block_text = "\n".join(lines)
    caption_match = CAPTION_PATTERN.search(block_text)
    caption = caption_match.group(1).strip() if caption_match else None
    includes = [adjust_include_path(line.strip(), input_dir, output_dir) for line in lines if "\\includegraphics" in line]
    if not includes:
        return []
    payload = ["\\begin{figure}[h]", "\\centering"]
    payload.extend(includes)
    if caption:
        payload.append(f"\\caption{{{caption}}}")
    payload.append("\\end{figure}")
    return payload


def adjust_include_path(line: str, input_dir: Path, output_dir: Path) -> str:
    def _replace(match: re.Match[str]) -> str:
        prefix, path, suffix = match.groups()
        stripped = path.strip()
        if not stripped or stripped.startswith(("/", "http://", "https://", "\\")):
            new_path = path
        else:
            repo_root = output_dir.parent
            rel_candidate = Path(stripped)
            bases = [input_dir]
            if not stripped.startswith(("../", "./")):
                bases.append(repo_root)
                if rel_candidate.parts and rel_candidate.parts[0] != "tex":
                    bases.append(repo_root / "tex")
            new_path = path
            for base in bases:
                candidate = (base / rel_candidate).resolve()
                if candidate.exists():
                    rel_path = os.path.relpath(candidate, output_dir)
                    new_path = rel_path.replace(os.sep, "/")
                    break
        return f"{prefix}{new_path}{suffix}"

    return INCLUDE_PATTERN.sub(_replace, line)


def build_frames(blocks: List[Block], base_title: str, input_dir: Path, output_dir: Path) -> List[str]:
    output: List[str] = []
    current_section: Optional[str] = None
    current_subsection: Optional[str] = None

    def frame_title() -> str:
        parts = [part for part in (current_section, current_subsection) if part]
        return " -- ".join(parts) if parts else base_title

    for block in blocks:
        if block.kind in {"notessection", "section", "chapter"}:
            current_section = block.title or current_section
            current_subsection = None
            if block.title:
                output.append(f"\\section{{{block.title}}}")
            continue
        if block.kind in {"subsection", "subsubsection"}:
            current_subsection = block.title or current_subsection
            if block.title:
                output.append(f"\\subsection{{{block.title}}}")
            continue
        summary = escape_tex(summarize_block(block.lines))
        output.append(f"\\begin{{frame}}[t]{{{frame_title()}}}")
        output.append("\\begin{itemize}")
        output.append(f"\\item {summary}")
        output.append("\\end{itemize}")
        if block.kind == "figure":
            payload = figure_payload(block.lines, input_dir, output_dir)
            if payload:
                output.extend(payload)
        output.append("\\end{frame}")
        output.extend(comment_block(block.lines))
        output.append("")
    return output


def write_beamer(blocks: List[Block], input_path: Path, output_path: Path) -> None:
    base_title = blocks[0].title if blocks and blocks[0].kind in {"notessection", "section", "chapter"} else input_path.stem
    header = build_header(base_title or input_path.stem, str(input_path))
    frames = build_frames(blocks, base_title or input_path.stem, input_path.parent, output_path.parent)
    footer = ["\\end{document}"]
    output_path.write_text("\n".join(header + [""] + frames + footer), encoding="utf-8")


def main() -> None:
    args = parse_args()
    if not args.input.is_file():
        raise FileNotFoundError(f"Input file not found: {args.input}")
    repo_root = Path(__file__).resolve().parents[1]
    default_output = repo_root / "slides" / f"{args.input.stem}.tex"
    output_path = args.output if args.output else default_output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = args.input.read_text(encoding="utf-8").splitlines()
    blocks = read_blocks(lines)
    if not blocks:
        raise ValueError("No content blocks detected in source file.")
    write_beamer(blocks, args.input, output_path)
    print(f"Created presentation at {output_path}")


if __name__ == "__main__":
    main()
