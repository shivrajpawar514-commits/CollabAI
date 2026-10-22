import os
import re
from typing import List, Dict, Any, Tuple


class ParsedPage:
    def __init__(self, page_number: int, text: str, heading: str = ""):
        self.page_number = page_number
        self.text = text.strip()
        self.heading = heading


class DocumentParser:
    """
    Multimodal document text extractor supporting PDF, Markdown, Plain Text, Code, and JSON files.
    """

    @classmethod
    def parse_file(cls, file_path: str, file_type: str = "") -> List[ParsedPage]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = (file_type or os.path.splitext(file_path)[1].replace(".", "")).lower()

        if ext == "pdf":
            return cls._parse_pdf(file_path)
        elif ext in ["md", "markdown"]:
            return cls._parse_markdown(file_path)
        elif ext in ["py", "js", "ts", "tsx", "jsx", "html", "css", "sql", "json"]:
            return cls._parse_code_or_text(file_path, is_code=True)
        else:
            return cls._parse_code_or_text(file_path, is_code=False)

    @classmethod
    def _parse_pdf(cls, file_path: str) -> List[ParsedPage]:
        pages: List[ParsedPage] = []
        
        # 1. Try PyMuPDF (fitz)
        try:
            import fitz
            doc = fitz.open(file_path)
            for i, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    pages.append(ParsedPage(page_number=i + 1, text=text))
            doc.close()
            if pages:
                return pages
        except Exception:
            pass

        # 2. Try pypdf
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(ParsedPage(page_number=i + 1, text=text))
            if pages:
                return pages
        except Exception:
            pass

        # 3. Fallback: Binary stream text extractor
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            # Extract plain text strings from PDF stream
            raw_text = content.decode("latin1", errors="ignore")
            # Look for BT...ET text blocks or ASCII substrings
            extracted = []
            for match in re.finditer(r"\(([^)]+)\)\s*Tj", raw_text):
                extracted.append(match.group(1))
            
            if not extracted:
                # Find all printable strings of length >= 4
                extracted = re.findall(r"[A-Za-z0-9 .,:;\-_/\\()'\"]{6,}", raw_text)
                
            combined = "\n".join(extracted[:500])
            if combined.strip():
                pages.append(ParsedPage(page_number=1, text=combined))
            else:
                pages.append(ParsedPage(page_number=1, text="PDF document uploaded. Content indexed."))
        except Exception:
            pages.append(ParsedPage(page_number=1, text="Uploaded document attachment."))

        return pages

    @classmethod
    def _parse_markdown(cls, file_path: str) -> List[ParsedPage]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        sections = re.split(r"(^#+\s+.*)", content, flags=re.MULTILINE)
        pages: List[ParsedPage] = []
        current_heading = "Overview"
        current_text = ""
        page_num = 1

        for part in sections:
            if re.match(r"^#+\s+", part):
                if current_text.strip():
                    pages.append(ParsedPage(page_number=page_num, text=current_text, heading=current_heading))
                    page_num += 1
                    current_text = ""
                current_heading = part.strip().lstrip("#").strip()
            else:
                current_text += "\n" + part

        if current_text.strip():
            pages.append(ParsedPage(page_number=page_num, text=current_text, heading=current_heading))

        return pages if pages else [ParsedPage(page_number=1, text=content)]

    @classmethod
    def _parse_code_or_text(cls, file_path: str, is_code: bool = False) -> List[ParsedPage]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Split long files into logical pseudo-pages (around 80 lines each)
        lines = content.splitlines()
        page_size = 80
        pages: List[ParsedPage] = []

        for i in range(0, len(lines), page_size):
            chunk_lines = lines[i : i + page_size]
            page_text = "\n".join(chunk_lines)
            heading = f"Lines {i+1}-{i+len(chunk_lines)}" if is_code else ""
            pages.append(ParsedPage(page_number=(i // page_size) + 1, text=page_text, heading=heading))

        return pages if pages else [ParsedPage(page_number=1, text=content)]
