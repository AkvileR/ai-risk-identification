import re
import sys
from pathlib import Path

import fitz


PDF_PATH = Path(__file__).resolve().parent / "AI-act-raw.pdf"
OUT_PATH = Path(__file__).resolve().parent / "ai_act.md"

FOOTER_PAT = re.compile(
    r"OJ L, [^\n]+\n+EN\n+ELI: http://[^\n]+\n+\d+/\d+\s*",
)
SOFT_HYPHEN_PAT = re.compile(r"­")
SMART_QUOTES = {
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "–": "-",
    "—": "-",
}


def load_pdf_text(path: Path) -> str:
    if len(sys.argv) > 1:
        candidate = Path(sys.argv[1])
        if candidate.exists():
            doc = fitz.open(candidate)
        else:
            raise FileNotFoundError(candidate)
    else:
        doc = fitz.open(path)
    pages = [p.get_text() for p in doc]
    doc.close()
    return "\n".join(pages)


def clean(text: str) -> str:
    text = FOOTER_PAT.sub("\n", text)
    text = SOFT_HYPHEN_PAT.sub("", text)
    for k, v in SMART_QUOTES.items():
        text = text.replace(k, v)
    text = text.replace("�", "'")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def extract_recitals(text: str) -> list[tuple[str, str]]:
    start = text.find("Whereas:")
    end = text.find("HAVE ADOPTED")
    body = text[start:end]
    pat = re.compile(r"(?m)^\((\d+)\)\s*$")
    matches = list(pat.finditer(body))
    sequential: list[re.Match] = []
    expected = 1
    for m in matches:
        n = int(m.group(1))
        if n == expected:
            sequential.append(m)
            expected += 1
    chunks: list[tuple[str, str]] = []
    for i, m in enumerate(sequential):
        n = int(m.group(1))
        s = m.end()
        e = sequential[i + 1].start() if i + 1 < len(sequential) else len(body)
        recital_text = body[s:e].strip()
        if recital_text:
            chunks.append((f"Recital {n}", recital_text))
    return chunks


def extract_articles(text: str) -> list[tuple[str, str]]:
    start = text.find("HAVE ADOPTED")
    annex_start = re.search(r"(?m)^ANNEX I\s*$", text)
    end = annex_start.start() if annex_start else len(text)
    body = text[start:end]
    pat = re.compile(r"(?m)^Article (\d+)\s*$")
    matches = list(pat.finditer(body))
    sequential: list[re.Match] = []
    expected = 1
    for m in matches:
        n = int(m.group(1))
        if n == expected:
            sequential.append(m)
            expected += 1
    chunks: list[tuple[str, str]] = []
    for i, m in enumerate(sequential):
        n = int(m.group(1))
        s = m.start()
        e = sequential[i + 1].start() if i + 1 < len(sequential) else len(body)
        article_text = body[s:e].strip()
        lines = article_text.split("\n", 2)
        title = lines[1].strip() if len(lines) > 1 else ""
        rest = lines[2].strip() if len(lines) > 2 else ""
        chunks.append((f"Art. {n}", f"**{title}**\n\n{rest}".strip()))
    return chunks


def extract_annexes(text: str) -> list[tuple[str, str]]:
    pat = re.compile(r"(?m)^ANNEX ([IVXLCDM]+)\s*$")
    matches = list(pat.finditer(text))
    seen_roman: set[str] = set()
    sequential: list[re.Match] = []
    for m in matches:
        roman = m.group(1)
        if roman in seen_roman:
            continue
        seen_roman.add(roman)
        sequential.append(m)
    chunks: list[tuple[str, str]] = []
    for i, m in enumerate(sequential):
        roman = m.group(1)
        s = m.start()
        e = sequential[i + 1].start() if i + 1 < len(sequential) else len(text)
        body = text[s:e].strip()
        lines = body.split("\n", 2)
        title = lines[1].strip() if len(lines) > 1 else ""
        rest = lines[2].strip() if len(lines) > 2 else ""
        chunks.append((f"Annex {roman}", f"**{title}**\n\n{rest}".strip()))
    return chunks


def main() -> None:
    raw = load_pdf_text(PDF_PATH)
    text = clean(raw)
    parts: list[tuple[str, str]] = []
    parts.extend(extract_recitals(text))
    parts.extend(extract_articles(text))
    parts.extend(extract_annexes(text))
    out = []
    for ref, body in parts:
        out.append(f"## {ref}\n\n{body}\n")
    OUT_PATH.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {len(parts)} chunks to {OUT_PATH}")


if __name__ == "__main__":
    main()
