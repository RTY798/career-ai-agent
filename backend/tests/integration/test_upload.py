"""TP1-3: PDF 上传完整流程（含异常路径）(P1)"""

import os
import io
import pytest
from fastapi import UploadFile
from app.services.pdf_parser import parse_pdf


SAMPLE_PDF_CONTENT = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (Hello World) Tj ET
endstream
endobj
xref
0 5
...
trailer<</Size 5/Root 1 0 R>>
%%EOF"""


class TestPDFParser:
    def test_parse_valid_pdf(self):
        """正常 PDF 提取"""
        text = parse_pdf(SAMPLE_PDF_CONTENT)
        assert isinstance(text, str)

    def test_parse_empty_bytes(self):
        with pytest.raises(RuntimeError):
            parse_pdf(b"")

    def test_parse_invalid_content(self):
        with pytest.raises(RuntimeError):
            parse_pdf(b"not a pdf at all")

    def test_parse_large_pdf(self):
        content = b"%" * (11 * 1024 * 1024)
        with pytest.raises(RuntimeError):
            parse_pdf(content)

    def test_clean_text_normalization(self):
        from app.services.pdf_parser import _clean_text
        text = "line1\n\n\n\nline2   spaced"
        cleaned = _clean_text(text)
        assert "\n\n\n" not in cleaned
        assert "  " not in cleaned
