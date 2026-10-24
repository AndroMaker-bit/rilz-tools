#!/usr/bin/env python3
"""
RILZ TOOLS - Multi-Purpose PDF Toolkit Engine
Features:
1. Compress PDF (deflate content streams, remove duplicate objects, strip metadata)
2. Merge multiple PDFs into one
3. Images to PDF (JPG, PNG, WebP to consolidated PDF)
4. Split PDF (extract page range or separate all pages)
5. Extract Text from PDF
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List
from PIL import Image
from pypdf import PdfReader, PdfWriter
from rich.console import Console

console = Console()


def format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{round(size / 1024, 1)} KB"
    else:
        return f"{round(size / (1024 * 1024), 2)} MB"


def compress_pdf_file(input_pdf: str, output_pdf: str, quality_preset: str = "medium") -> Dict[str, Any]:
    """
    Compresses a PDF file:
    - Downscales and re-compresses embedded raster images (JPEG quality / max resolution capping)
    - Removes duplicate identical objects and unreferenced orphan streams
    - Deflates content streams with zlib (level 9)
    - Fallback protection: ensures the output file is never larger than the original input!
    """
    if not os.path.exists(input_pdf):
        return {"success": False, "error": "File PDF input tidak ditemukan."}

    orig_size = os.path.getsize(input_pdf)
    if orig_size == 0:
        return {"success": False, "error": "File PDF kosong (0 bytes)."}

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf)), exist_ok=True)

    # Preset settings: (jpeg_quality, max_dimension)
    presets = {
        "low": (40, 1024),      # Maximum compression / smallest file size
        "medium": (65, 1600),   # Standard / balanced
        "high": (82, 2400),     # Mild compression / crisp print quality
    }
    q, max_dim = presets.get(str(quality_preset).lower(), (65, 1600))

    try:
        reader = PdfReader(input_pdf)
        total_pages = len(reader.pages)
        writer = PdfWriter(clone_from=input_pdf)

        images_processed = 0
        # 1. Compress embedded raster images
        for page in writer.pages:
            try:
                for img_obj in page.images:
                    try:
                        pil_img = img_obj.image
                        w, h = pil_img.size

                        # Downscale oversized images
                        if max(w, h) > max_dim:
                            pil_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

                        # If RGBA is completely opaque, convert to RGB for higher compression
                        if pil_img.mode == "RGBA":
                            try:
                                extrema = pil_img.getextrema()
                                if extrema and len(extrema) >= 4 and extrema[3][0] == 255:
                                    pil_img = pil_img.convert("RGB")
                            except Exception:
                                pass

                        img_obj.replace(pil_img, quality=q)
                        images_processed += 1
                    except Exception:
                        continue
            except Exception:
                continue

        # 2. Compress identical and unreferenced objects
        try:
            # pypdf 6+ syntax
            writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
        except TypeError:
            try:
                # legacy pypdf syntax
                writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
            except Exception:
                pass
        except Exception:
            pass

        # 3. Maximum deflate compression on page content streams
        for page in writer.pages:
            try:
                page.compress_content_streams(level=9)
            except Exception:
                pass

        # 4. Write out candidate compressed PDF
        with open(output_pdf, "wb") as f_out:
            writer.write(f_out)

        comp_size = os.path.getsize(output_pdf)

        # 5. Fallback protection: Never return a file that got bigger!
        if comp_size >= orig_size:
            # Original was already optimal. Preserve original bytes!
            shutil.copyfile(input_pdf, output_pdf)
            comp_size = orig_size
            saved_bytes = 0
            saved_pct = 0.0
            is_optimal = True
        else:
            saved_bytes = orig_size - comp_size
            saved_pct = round((saved_bytes / orig_size) * 100, 1)
            is_optimal = False

        return {
            "success": True,
            "filepath": output_pdf,
            "filename": os.path.basename(output_pdf),
            "orig_size": orig_size,
            "comp_size": comp_size,
            "orig_str": format_bytes(orig_size),
            "comp_str": format_bytes(comp_size),
            "saved_bytes": saved_bytes,
            "saved_percent": saved_pct,
            "is_optimal": is_optimal,
            "pages": total_pages,
            "images_compressed": images_processed,
        }
    except Exception as e:
        return {"success": False, "error": f"Gagal mengompres PDF: {e}"}


def merge_pdf_files(pdf_paths: List[str], output_pdf: str) -> Dict[str, Any]:
    """
    Merges multiple PDF files into a single PDF document.
    """
    if not pdf_paths:
        return {"success": False, "error": "Tidak ada file PDF yang dipilih untuk digabungkan."}

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf)), exist_ok=True)
    merger = PdfWriter()
    total_pages = 0
    merged_count = 0

    try:
        for path in pdf_paths:
            if not os.path.exists(path):
                continue
            reader = PdfReader(path)
            for page in reader.pages:
                merger.add_page(page)
                total_pages += 1
            merged_count += 1

        if merged_count == 0:
            return {"success": False, "error": "Tidak ada PDF valid yang bisa digabung."}

        with open(output_pdf, "wb") as f_out:
            merger.write(f_out)

        size = os.path.getsize(output_pdf)
        return {
            "success": True,
            "filepath": output_pdf,
            "filename": os.path.basename(output_pdf),
            "total_files": merged_count,
            "total_pages": total_pages,
            "size_bytes": size,
            "size_str": format_bytes(size)
        }
    except Exception as e:
        return {"success": False, "error": f"Gagal menggabungkan PDF: {e}"}


def images_to_pdf_file(image_paths: List[str], output_pdf: str) -> Dict[str, Any]:
    """
    Converts one or multiple images (JPG, PNG, WebP) into a consolidated PDF.
    """
    if not image_paths:
        return {"success": False, "error": "Tidak ada file gambar yang diberikan."}

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf)), exist_ok=True)
    valid_images = []
    first_image = None

    for path in image_paths:
        if not os.path.exists(path):
            continue
        try:
            img = Image.open(path)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            if first_image is None:
                first_image = img
            else:
                valid_images.append(img)
        except Exception:
            pass

    if not first_image:
        return {"success": False, "error": "Tidak ada file gambar yang valid."}

    try:
        first_image.save(output_pdf, save_all=True, append_images=valid_images)
        size = os.path.getsize(output_pdf)
        total_pages = len(valid_images) + 1
        return {
            "success": True,
            "filepath": output_pdf,
            "filename": os.path.basename(output_pdf),
            "total_pages": total_pages,
            "size_bytes": size,
            "size_str": format_bytes(size)
        }
    except Exception as e:
        return {"success": False, "error": f"Gagal membuat PDF dari gambar: {e}"}


def extract_text_from_pdf(pdf_path: str, output_txt: str = None) -> str:
    """Extract all text from a PDF file."""
    if not os.path.exists(pdf_path):
        return ""

    try:
        reader = PdfReader(pdf_path)
        all_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            all_text.append(f"--- Halaman {i+1} ---\n{text}")

        full_content = "\n\n".join(all_text)
        if output_txt:
            with open(output_txt, "w", encoding="utf-8") as f:
                f.write(full_content)
        return full_content
    except Exception:
        return ""
