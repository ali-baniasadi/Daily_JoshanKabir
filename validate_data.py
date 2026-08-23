import json
from pathlib import Path
p=Path(__file__).resolve().parent/"data"/"joshan_kabir.json"
data=json.loads(p.read_text(encoding="utf-8"))
assert len(data)==100, f"Expected 100, got {len(data)}"
assert [x["number"] for x in data]==list(range(1,101)), "Numbers are not 1..100"
assert all(x.get("arabic") and x.get("translation") for x in data), "Incomplete section"
print("OK: all 100 sections are present and ordered.")
