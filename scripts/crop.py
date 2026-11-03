"""Crop a template: python scripts/crop.py SRC.png X Y W H OUT.png (coordinates in the 720x1280 frame)."""

import sys

import cv2

src, x, y, w, h, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
cv2.imwrite(out, cv2.imread(src)[y:y + h, x:x + w])
print(out)
