"""Download the PaddleOCR ONNX models MaaFramework uses into resource/model/ocr/.

Detection: PP-OCRv4 (language-agnostic). Recognition: PP-OCRv4 English.
Source: https://github.com/MaaXYZ/MaaCommonAssets (OCR/). The models are gitignored; run this once per clone.
"""

import sys
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/MaaXYZ/MaaCommonAssets/main/OCR/ppocr_v4"
FILES = {
    "det.onnx": f"{BASE}/zh_cn/det.onnx",
    "rec.onnx": f"{BASE}/en_us/rec.onnx",
    "keys.txt": f"{BASE}/en_us/keys.txt",
}
DEST = Path(__file__).resolve().parent.parent / "resource" / "model" / "ocr"


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        target = DEST / name
        if target.exists() and "--force" not in sys.argv:
            print(f"have {target.name}")
            continue
        print(f"fetching {name}")
        urllib.request.urlretrieve(url, target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
