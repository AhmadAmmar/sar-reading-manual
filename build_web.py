"""Web edition, through the shared converter. Needs a finished PDF build first, because numbers come from tex/main.aux.

    python build_web.py
"""
from pathlib import Path

from research_helpers import tex_web as T

HERE = Path(__file__).resolve().parent
SITE = Path.home() / "dev/AhmadAmmar.github.io"
TEX = HERE / "tex"
SNIPPET = r"\newcommand{\snippetcaption}[1]{\textbf{From the code:} \texttt{#1}}"
PREAMBLE = [
    r"\documentclass[11pt,a4paper]{article}",
    r"\usepackage[T1]{fontenc}",
    r"\usepackage{lmodern,caption,amsmath,graphicx,booktabs,xcolor,listings,float,tabularx}",
    r"\usepackage[margin=24mm]{geometry}",
    r"\graphicspath{{../figures/}}",
    r"\input{generated/values.tex}",
    SNIPPET,
]
PROJECT = T.Project(
    root=TEX, aux=TEX / "main.aux", url="/teaching/sar/", out=SITE / "src/sar", figures=SITE / "teaching/sar/fig",
    chapters=[T.Chapter("reading-radar-london", TEX / "ch_basics.tex"), T.Chapter("mapping-a-flood-sindh", TEX / "ch_flood.tex")],
    preamble=PREAMBLE,
    macros=(TEX / "generated/values.tex").read_text(encoding="utf8") + "\n" + SNIPPET + "\n",
    description="{label}: Reading radar images, a working manual.", search=[TEX], definition_inputs=("values.tex",), inline_generated=("snip_", "london_places"),
    index_head=["---", "slug: index", "title: Reading radar images", "description: Reading Sentinel-1 radar images step by step, on real places.", "---", "", "A working manual for reading Sentinel-1 radar images, with each step shown on a real place. Read it chapter by chapter, or the [whole manual on one page](full/). You can also download the [PDF](/files/Reading_radar_images_Ahmad_Ammar.pdf), and the code is on [GitHub](https://github.com/AhmadAmmar/sar-reading-manual).", ""],
)
if __name__ == "__main__":
    print(T.build_figures(PROJECT))
    T.build_pages(PROJECT)
    print(sorted(p.name for p in PROJECT.out.glob("*")), len(list(PROJECT.figures.glob("*"))))
