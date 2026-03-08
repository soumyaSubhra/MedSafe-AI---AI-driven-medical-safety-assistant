# ocr_reader.py
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR"
from typing import Union
from PIL import Image, ImageOps
import pytesseract
import io
import os

# If tesseract is not on PATH, uncomment and set correct path:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def _open_image_from_arg(arg) -> Image.Image:
    """
    Accepts: filepath (str), file-like object, bytes, or BytesIO.
    Returns PIL Image.
    """
    if isinstance(arg, str):
        return Image.open(arg)
    # file-like with .read()
    if hasattr(arg, "read"):
        # reset pointer if possible
        try:
            arg.seek(0)
        except Exception:
            pass
        return Image.open(arg)
    # bytes object
    if isinstance(arg, (bytes, bytearray)):
        return Image.open(io.BytesIO(arg))
    raise ValueError("Unsupported input type for read_prescription")

def read_prescription(input_data: Union[str, bytes, object]) -> str:
    """
    Robust OCR wrapper. Returns extracted plain text.
    input_data may be:
      - path string,
      - file-like object with read(),
      - bytes (raw image bytes)
    """
    try:
        img = _open_image_from_arg(input_data)
    except Exception as e:
        raise RuntimeError(f"Failed opening image: {e}")

    # convert to grayscale and increase contrast a bit for better OCR
    try:
        img = ImageOps.exif_transpose(img)  # correct orientation from EXIF
        img = img.convert("L")  # grayscale
        # optional: resize small images (uncomment if needed)
        # w,h = img.size
        # if w < 1000:
        #     img = img.resize((int(w*1.5), int(h*1.5)), Image.LANCZOS)
    except Exception:
        pass

    # pytesseract call
    try:
        text = pytesseract.image_to_string(img, lang="eng", config="--psm 6")
        return text
    except Exception as e:
        raise RuntimeError(f"pytesseract OCR failed: {e}")