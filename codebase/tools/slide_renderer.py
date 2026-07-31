from __future__ import annotations

from pathlib import Path
import fitz  # PyMuPDF


def render_pdf_page_to_bytes(pdf_path: Path | str, page_num: int) -> bytes:
    """Mở PDF và kết xuất trang chỉ định thành dữ liệu ảnh PNG dưới dạng bytes."""
    try:
        doc = fitz.open(pdf_path)
        if page_num < 1 or page_num > len(doc):
            raise IndexError(f"Trang {page_num} nằm ngoài dải của tài liệu (1-{len(doc)})")
        page = doc.load_page(page_num - 1)
        pix = page.get_pixmap(dpi=150)
        return pix.tobytes("png")
    except Exception as e:
        raise RuntimeError(f"Lỗi khi render trang slide PDF {page_num}: {e}")


def get_pdf_page_count(pdf_path: Path | str) -> int:
    """Trả về tổng số trang của file PDF."""
    try:
        doc = fitz.open(pdf_path)
        return len(doc)
    except Exception:
        return 0
