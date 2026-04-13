#!/usr/bin/env python3
"""Rough parser for 2016 交換考題 詳解.pdf.

PDF format is inconsistent (merged from multiple hospitals).
This produces a best-effort initial JSON — physicians will review
and correct content via the web editing interface.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import fitz  # PyMuPDF

PDF_PATH = Path(__file__).parent.parent.parent / "0筆記" / "Radiology" / "3. Resources" / "論文s" / "交換考" / "2016 交換考題 詳解.pdf"
OUTPUT_DIR = Path(__file__).parent.parent / "data"
IMAGE_DIR = OUTPUT_DIR / "images" / "2016"
JSON_OUTPUT = OUTPUT_DIR / "2016.json"


def extract_text(pdf_path: str) -> str:
    """Extract text via pdftotext with fallback."""
    try:
        result = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True)
        if result.returncode == 0 and result.stdout:
            try:
                return result.stdout.decode("utf-8")
            except UnicodeDecodeError:
                return result.stdout.decode("utf-8", errors="replace")
    except FileNotFoundError:
        pass
    doc = fitz.open(pdf_path)
    text = "\n".join(p.get_text() for p in doc)
    doc.close()
    return text


def extract_images(pdf_path: str, image_dir: Path) -> int:
    """Extract all images from PDF."""
    image_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    n = 0
    for page in doc:
        for info in page.get_images(full=True):
            try:
                base = doc.extract_image(info[0])
                if base:
                    n += 1
                    fn = f"img-{n:03d}.{base.get('ext', 'png')}"
                    (image_dir / fn).write_bytes(base["image"])
            except Exception:
                pass
    doc.close()
    return n


def rough_split(text: str) -> list:
    """Split text into rough question blocks.

    Uses a simple heuristic: find lines that look like answer + question starts.
    Accept imperfect results — physicians will fix via editor.
    """
    lines = text.split("\n")
    # Pattern: standalone answer letter at start of line, followed by question text
    # Matches: "D Concerning..." or "(A)" on its own line or "(C)\nThe diagnostic..."
    blocks = []
    current = {"lines": [], "answer": "?"}

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for answer line patterns:
        # 1. Bare letter: "D Concerning congenital..."
        # 2. Parenthesized on own line: "(A)" then question on next line
        # 3. Parenthesized inline: "(C) The diagnostic quality..."

        new_question = False
        answer = None

        # Pattern 1: ^[A-D] [A-Z] (bare letter + space + capital = new question)
        m = re.match(r"^([A-D])\s+([A-Z])", line)
        if m:
            # Exclude explanation lines like "A Incorrect" or "D Correct"
            rest = line[2:].strip()
            if not re.match(r"^(Incorrect|Correct|incorrect|correct)", rest):
                # Check: does the text within 30 lines contain (A) (B) option markers?
                lookahead = "\n".join(lines[i:i+30])
                if re.search(r"[\(（][A-D][\)）]", lookahead):
                    new_question = True
                    answer = m.group(1)
                    line = line[2:].strip()  # Remove answer letter

        # Pattern 2: ^(A)$ on its own line
        if not new_question:
            m = re.match(r"^[\(（]([A-D])[\)）]\s*$", line)
            if m:
                # Look ahead: next non-empty line should be question text
                lookahead = "\n".join(lines[i+1:i+30])
                if re.search(r"[\(（][A-D][\)）]", lookahead):
                    new_question = True
                    answer = m.group(1)
                    i += 1  # Skip this line, question text is on next line
                    if i < len(lines):
                        line = lines[i].strip()
                    else:
                        line = ""

        if new_question and current["lines"]:
            # Save previous block
            blocks.append(current)
            current = {"lines": [], "answer": answer or "?"}

        if new_question and not current["lines"]:
            current["answer"] = answer or "?"

        if line:
            current["lines"].append(line)

        i += 1

    if current["lines"]:
        blocks.append(current)

    return blocks


def parse_block(block: dict, number: int) -> dict:
    """Parse a rough block into a question structure."""
    text = "\n".join(block["lines"])
    answer = block["answer"]

    # Try to find options (A)-(D) and split
    options = []
    question_text = text
    explanation = ""
    reference = ""

    # Find option markers
    opt_markers = list(re.finditer(r"[\(（]([A-D])[\)）]\s*", text))
    if len(opt_markers) >= 2:
        # Question text = everything before first option
        question_text = text[:opt_markers[0].start()].strip()

        # Extract options
        seen = set()
        for idx, m in enumerate(opt_markers):
            letter = m.group(1)
            if letter in seen:
                continue
            seen.add(letter)
            start = m.end()
            # End at next option marker or end of relevant area
            end = opt_markers[idx + 1].start() if idx + 1 < len(opt_markers) else len(text)
            opt_text = text[start:end].strip()
            # Truncate at double newline (likely explanation/reference start)
            cut = re.search(r"\n\s*\n", opt_text)
            if cut:
                opt_text = opt_text[:cut.start()]
            opt_text = re.sub(r"\s+", " ", opt_text).strip()
            options.append({"letter": letter, "text": opt_text[:500]})

        # Everything after last option = explanation (includes reference)
        # Put ALL remaining text into explanation for physician review
        if opt_markers:
            last = opt_markers[-1]
            remaining = text[last.end():]
            # Skip past last option's text (to first double newline)
            cut = re.search(r"\n\s*\n", remaining)
            if cut:
                last_opt_text = remaining[:cut.start()].strip()
                # Update last option text if it was truncated
                if options and not options[-1]["text"]:
                    options[-1]["text"] = re.sub(r"\s+", " ", last_opt_text)[:500]
                explanation = remaining[cut.end():].strip()
            else:
                explanation = remaining.strip()
    else:
        # No options found — store entire text as question, mark for review
        question_text = re.sub(r"\s+", " ", text).strip()

    # Pad options
    existing = {o["letter"] for o in options}
    for letter in "ABCD":
        if letter not in existing:
            options.append({"letter": letter, "text": ""})
    options.sort(key=lambda o: o["letter"])

    question_text = re.sub(r"\s+", " ", question_text).strip()

    return {
        "id": f"2016-{number:03d}",
        "year": 2016,
        "number": number,
        "subspecialty": "Unknown",
        "subspecialty_confidence": "auto",
        "questionText": question_text[:2000],
        "options": options[:4],
        "correctAnswer": answer,
        "reference": reference[:1000],
        "explanation": explanation[:3000],
        "images": [],
        "concepts": [],
        "checked": False,
    }


def main():
    pdf_path = str(PDF_PATH) if PDF_PATH.exists() else (sys.argv[1] if len(sys.argv) > 1 else None)
    if not pdf_path or not Path(pdf_path).exists():
        print(f"ERROR: PDF not found: {PDF_PATH}")
        sys.exit(1)

    print(f"Parsing: {Path(pdf_path).name}")

    # Text
    print("[1/3] Extracting text...")
    text = extract_text(pdf_path)
    print(f"  {len(text)} chars")

    # Images
    print("[2/3] Extracting images...")
    n_img = extract_images(pdf_path, IMAGE_DIR)
    print(f"  {n_img} images")

    # Questions
    print("[3/3] Splitting into questions...")
    blocks = rough_split(text)
    print(f"  {len(blocks)} question blocks")

    questions = [parse_block(b, i + 1) for i, b in enumerate(blocks)]

    # Output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = {"year": 2016, "totalQuestions": len(questions), "questions": questions}
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Summary
    has_opts = sum(1 for q in questions if len([o for o in q["options"] if o["text"]]) >= 2)
    has_expl = sum(1 for q in questions if q["explanation"])
    has_ans = sum(1 for q in questions if q["correctAnswer"] != "?")
    print(f"\n  Output: {JSON_OUTPUT}")
    print(f"  Questions: {len(questions)}")
    print(f"  With 2+ options: {has_opts}")
    print(f"  With explanation: {has_expl}")
    print(f"  With answer: {has_ans}")
    print(f"  Images: {n_img}")
    print(f"\n  Note: Content needs physician review via web editor.")


if __name__ == "__main__":
    main()
