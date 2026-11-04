"""Print every OCR result MaaFramework finds in a region: python scripts/ocr.py IMAGE.png [X Y W H]"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.core.replay import ImageDevice  # noqa: E402
from sxs.core.state import StateDetector  # noqa: E402

dev = ImageDevice()
dev.set_frame(sys.argv[1])
det = StateDetector(dev)
roi = list(map(int, sys.argv[2:6])) if len(sys.argv) >= 6 else [0, 0, 720, 1280]
override = {"Debug.OCR": {"recognition": "OCR", "roi": roi, "only_rec": False, "pre_delay": 0, "post_delay": 0}}
detail = det.tasker.post_task("Debug.OCR", override).wait().get()
for node in detail.nodes:
    for r in node.recognition.all_results:
        print(r.box, round(r.score, 3), r.text)
