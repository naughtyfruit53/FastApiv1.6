# insert_drop_before_create.py
import re
from pathlib import Path

p = Path("migrations/versions/ebd28dc6f2b6_initial_new_final.py")
if not p.exists():
    raise SystemExit(f"File not found: {p}")

txt = p.read_text(encoding="utf-8")

# match op.create_index('idx_name', ... or op.create_index(op.f('ix_name'), ...
pat = re.compile(r"(op\.create_index\(\s*(?:op\.f\(\s*)?([\"'])(idx_[^\"']+)\1)")

def repl(m):
    full = m.group(1)
    idx_name = m.group(3)
    drop = f"op.execute('DROP INDEX IF EXISTS {idx_name}')\n    "
    return drop + full

txt2 = pat.sub(repl, txt)

if txt == txt2:
    print("No op.create_index index lines found to patch.")
else:
    bak = p.with_suffix(".py.bak")
    bak.write_text(txt, encoding="utf-8")
    p.write_text(txt2, encoding="utf-8")
    print("Patched file and created backup:", bak)
