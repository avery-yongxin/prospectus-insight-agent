from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Iterable


class PDFParseError(RuntimeError):
    """Raised when a prospectus PDF cannot be parsed into usable text."""


def _normalize_line(line: str) -> str:
    line = re.sub(r"\s+", " ", line).strip()
    return line


def _remove_repeated_lines(pages: list[list[str]], max_line_length: int = 60) -> list[list[str]]:
    all_lines: list[str] = []
    for page_lines in pages:
        all_lines.extend(line for line in page_lines if 0 < len(line) <= max_line_length)

    repeated = {
        line
        for line, count in Counter(all_lines).items()
        if count >= 3 and not re.search(r"(风险|财务|业务|募集|公司|发行)", line)
    }
    return [[line for line in page_lines if line not in repeated] for page_lines in pages]


def _clean_pages(raw_pages: Iterable[str]) -> str:
    page_lines: list[list[str]] = []
    for page_text in raw_pages:
        lines = [_normalize_line(line) for line in page_text.splitlines()]
        lines = [line for line in lines if line]
        page_lines.append(lines)

    page_lines = _remove_repeated_lines(page_lines)
    chunks: list[str] = []
    for page_number, lines in enumerate(page_lines, start=1):
        body = "\n".join(lines).strip()
        if body:
            chunks.append(f"\n\n[第 {page_number} 页]\n{body}")
    return "\n".join(chunks).strip()


def extract_pdf_text(pdf_path: str | Path, output_path: str | Path = "outputs/extracted_text.txt") -> str:
    """Extract text from a PDF and save a cleaned page-marked text file."""
    source = Path(pdf_path)
    if not source.exists():
        raise PDFParseError(f"PDF 文件不存在：{source}")
    if source.stat().st_size == 0:
        raise PDFParseError("PDF 文件为空，请上传有效的招股说明书 PDF。")

    try:
        import fitz

        doc = fitz.open(source)
    except ModuleNotFoundError as exc:
        raise PDFParseError("未安装 pymupdf 依赖，请先运行 pip install -r requirements.txt。") from exc
    except Exception as exc:
        raise PDFParseError(f"PDF 打开失败：{exc}") from exc

    try:
        raw_pages = [page.get_text("text") for page in doc]
    finally:
        doc.close()

    cleaned_text = _clean_pages(raw_pages)
    if len(cleaned_text) < 100:
        raise PDFParseError("未能提取到足够文本。该 PDF 可能是扫描版，请先 OCR 后再上传。")

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(cleaned_text, encoding="utf-8")
    return cleaned_text
