from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "3 - MANUSCRITO" / "1-MARKDOWN" / "3-SCRIPTS"

# Heurísticas simples: palavras/PT comuns + caracteres acentuados.
PORTUGUESE_TOKENS = [
    # Preferir termos distintivos em PT (evita falsos positivos com inglês).
    "controle",  # 'Control' em inglês não contém este token
    "tratamento",
    "germinação",
    "germinacao",
    "comprimento",
    "inibição",
    "inibicao",
    "número",
    "numero",
    "avaliação",
    "avaliacao",
    "parte aérea",
    "parte aerea",
    "radícula",
    "radicula",
    "úmido",
    "umido",
    "dependência",
    "dependencia",
    "núcleo",
    "nucleo",
    "tempo (dias)",
    "curvas de",
]

ACCENT_RE = re.compile(r"[áàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ]")

# Funções/métodos comuns que escrevem texto em figura.
TEXT_FUNCS = {
    "set_xlabel",
    "set_ylabel",
    "set_title",
    "xlabel",
    "ylabel",
    "title",
    "suptitle",
    "text",
    "figtext",
    "annotate",
}


# Checagem focada nos scripts que geram as figuras do manuscrito.
# (Evita sinalizar scripts auxiliares/antigos que não entram no DOCX EN.)
SCRIPT_ALLOWLIST = {
    "plot_absorption.py",
    "plot_bandeja_bars.py",
    "plot_growth.py",
    "plot_ivg.py",
    "plot_raincloud.py",
    "plot_tga_typha.py",
    "plot_ftir_typha.py",
    "analyze_germination_survival.py",
    "analyze_bandeja_mixed_pca.py",
}


@dataclass(frozen=True)
class Finding:
    path: Path
    lineno: int
    col: int
    call: str
    text: str
    reason: str


def _is_suspicious(text: str) -> str | None:
    t = text.strip()
    if not t:
        return None

    low = t.casefold()
    for tok in PORTUGUESE_TOKENS:
        if tok in low:
            return f"token:{tok}"

    if ACCENT_RE.search(t):
        # acentos em inglês são raros (mas possíveis). sinaliza como suspeito.
        return "accent"

    return None


def _extract_literal_strings(node: ast.AST) -> list[str]:
    # Captura literais e partes constantes de f-strings.
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]

    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
        if parts:
            return ["".join(parts)]

    return []


def _call_name(call: ast.Call) -> str | None:
    f = call.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return None


def scan_file(path: Path) -> list[Finding]:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(path))

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        name = _call_name(node)
        if not name or name not in TEXT_FUNCS:
            continue

        # inspeciona somente o 1º argumento posicional (onde geralmente está o texto)
        if not node.args:
            continue

        texts: list[str] = []
        texts.extend(_extract_literal_strings(node.args[0]))

        # também considera kwargs comuns como s=, text=, label=
        for kw in node.keywords or []:
            if not kw.arg:
                continue
            if kw.arg in {"s", "text", "label"}:
                texts.extend(_extract_literal_strings(kw.value))

        for txt in texts:
            reason = _is_suspicious(txt)
            if reason:
                findings.append(
                    Finding(
                        path=path,
                        lineno=getattr(node, "lineno", 1),
                        col=getattr(node, "col_offset", 0),
                        call=name,
                        text=txt,
                        reason=reason,
                    )
                )

    return findings


def main() -> int:
    if not SCRIPTS_DIR.exists():
        raise SystemExit(f"Scripts dir not found: {SCRIPTS_DIR}")

    py_files = sorted(p for p in SCRIPTS_DIR.glob("*.py") if p.name in SCRIPT_ALLOWLIST)
    all_findings: list[Finding] = []
    for p in py_files:
        all_findings.extend(scan_file(p))

    if not all_findings:
        print("OK: não encontrei strings suspeitas (PT/acentos) em chamadas de texto de figuras nos scripts.")
        return 0

    print("ATENÇÃO: possíveis strings em PT (ou com acentos) encontradas em texto de figura:")
    for f in sorted(all_findings, key=lambda x: (str(x.path), x.lineno, x.col)):
        rel = f.path.relative_to(REPO_ROOT)
        short = f.text.replace("\n", " ")
        if len(short) > 140:
            short = short[:137] + "..."
        print(f"- {rel}:{f.lineno}:{f.col} | {f.call} | {f.reason} | {short!r}")

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
