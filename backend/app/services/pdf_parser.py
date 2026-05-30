"""PyMuPDF 简历解析服务"""

import os
import tempfile

import fitz


def parse_pdf(file_bytes: bytes) -> str:
    """解析 PDF 文件内容，返回纯文本"""
    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(file_bytes)
        tmp.close()

        doc = fitz.open(tmp.name)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()

        text = "\n".join(text_parts)
        return _clean_text(text)

    except Exception as e:
        raise RuntimeError(f"PDF 解析失败: {e}") from e

    finally:
        if tmp and os.path.exists(tmp.name):
            os.unlink(tmp.name)


def _clean_text(text: str) -> str:
    """清理文本：归一化空白"""
    import re

    # 合并连续换行为双换行（段落分隔）
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 合并多空格为单空格
    text = re.sub(r"[ ]{2,}", " ", text)
    # 行首尾空白清理
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines)


def parse_pdf_file(file_path: str) -> str:
    """从文件路径解析 PDF"""
    with open(file_path, "rb") as f:
        return parse_pdf(f.read())
