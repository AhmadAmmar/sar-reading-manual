"""Numbers and code excerpts for the manual, from the analyses and the code itself."""
import json
from pathlib import Path

from research_helpers.autotex import write_values
from research_helpers.snippets import around_listing, function_listing
from sarlib import DATA, GEN

SRC = Path(__file__).parent
values = {**json.loads((DATA / "london_stats.json").read_text()), **json.loads((DATA / "sindh_stats.json").read_text())}
write_values(GEN / "values.tex", {k: (v if not isinstance(v, float) else (v, 2 if "std" in k else 1)) for k, v in values.items()})
function_listing(SRC / "sarlib.py", "s1", GEN / "snip_s1.tex", "src/sarlib.py, s1()")
function_listing(SRC / "sarlib.py", "mean_db", GEN / "snip_mean.tex", "src/sarlib.py, mean_db()")
function_listing(SRC / "sarlib.py", "otsu", GEN / "snip_otsu.tex", "src/sarlib.py, otsu()")
around_listing(SRC / "02_sindh_flood.py", r"^flood = ", GEN / "snip_rule.tex", 2, 1, "src/02_sindh_flood.py")
