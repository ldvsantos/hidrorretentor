from __future__ import annotations

from pathlib import Path
import re


def extract_abstract_words(markdown_text: str) -> int | None:
    match = re.search(
        r"(?ms)^#\s+Abstract\b.*?\n\n(.*?)(?=^##\s+Keywords\b)",
        markdown_text,
    )
    if not match:
        return None

    abstract = match.group(1).strip()
    abstract = re.sub(r"\[@[^\]]+\]", "", abstract)  # remove citations
    abstract = re.sub(r"\$[^$]*\$", "", abstract)  # remove inline math

    words = re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?", abstract)
    return len(words)


def main() -> None:
    base = Path(__file__).resolve().parents[1] / "3 - MANUSCRITO" / "1-MARKDOWN" / "1-MANUSCRITOS"

    en_path = base / "Hidrorretentor_Taboa_EN.md"
    highlights_path = base / "Hidrorretentor_Taboa_highlights.txt"

    en_text = en_path.read_text(encoding="utf-8")
    wc = extract_abstract_words(en_text)

    print(f"EN abstract word count (approx): {wc if wc is not None else 'NOT FOUND'}")

    bullets = [line.strip() for line in highlights_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print("\nHighlights bullets / char counts:")
    for i, bullet in enumerate(bullets, 1):
        t = re.sub(r"^[-*•\u2022]\s+", "", bullet)
        print(f"{i}: {len(t)} chars | {t}")


if __name__ == "__main__":
    main()
