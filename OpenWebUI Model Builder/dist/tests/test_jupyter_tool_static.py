
from __future__ import annotations

import importlib.util
from pathlib import Path


TOOL_PATH = Path(__file__).resolve().parents[1] / "tools" / "jupyter" / "jupyter_tool.py"
spec = importlib.util.spec_from_file_location("jupyter_tool", TOOL_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

blocked_samples = [
    "import os\nos.system('dir')",
    "!dir",
    "import requests\nrequests.get('http://example.invalid')",
    "open('secret.txt').read()",
    "import subprocess\nsubprocess.run(['dir'])",
]
for sample in blocked_samples:
    try:
        module._validate_python_code(sample)
    except module.SecurityPolicyError:
        continue
    raise AssertionError(f"Sample was not blocked: {sample!r}")

module._validate_python_code("import pandas as pd\nx = 1 + 1\nprint(x)")
print("static security policy checks passed")
