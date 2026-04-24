"""conftest — 将 scripts/ 加入 Python 路径以便测试导入。"""

from __future__ import annotations

import sys
from pathlib import Path

# 将 scripts/ 目录加入 sys.path，使测试可以 import generate_codemaps
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
