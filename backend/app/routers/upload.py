"""PDF 上传解析端点"""

import logging

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.services.pdf_parser import parse_pdf

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """上传 PDF 简历，提取文本内容"""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="请上传 PDF 文件")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件超过 10MB 限制")

    try:
        text = parse_pdf(contents)
        if not text.strip():
            raise HTTPException(status_code=400, detail="无法从 PDF 中提取文本，请确认文件包含可识别的文字内容")
        return {"text": text[:15000], "filename": file.filename, "size": len(text)}
    except Exception as e:
        logger.error("pdf_parse_failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=f"PDF 解析失败: {str(e)}")
