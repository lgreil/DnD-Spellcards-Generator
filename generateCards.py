import json

TEMPLATE_HEADER = r"""
\documentclass[a4paper]{article}
\usepackage[margin=0.5cm]{geometry}
\usepackage{fontspec}
\usepackage{tcolorbox}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{fontawesome5}

\setmainfont{Inter}
\newfontfamily\titlefont{Cinzel}

\definecolor{evocation}{HTML}{D97706}
\definecolor{illusion}{HTML}{7C3AED}
\definecolor{necromancy}{HTML}{374151}

\newtcolorbox{spellcard}[1][]{
    width=7.4cm,
    height=10.5cm,
    colback=white,
    colframe=black,
    boxrule=0.5pt,
    arc=3mm,
    auto outer arc,
    left=2mm,
    right=2mm,
    top=2mm,
    bottom=2mm,
}

\newcommand{\spell}[11]{
\begin{spellcard}
{\titlefont\color{#1}\textbf{#2}}\\
\small Stufe #3 • #4

\vspace{2mm}\hrule\vspace{1mm}

\small
\faClock\ #5 \hfill \faRulerHorizontal\ #6\\
\faBullseye\ #7 \hfill \faHourglassHalf\ #8\\
\faCubes\ #9

\vspace{1mm}\hrule\vspace{1mm}

#10

\vspace{1mm}\hrule\vspace{1mm}

\small ↑ Höhere Grade: #11
\end{spellcard}
}

\begin{document}
\centering
\begin{tabular}{ccc}
"""

TEMPLATE_FOOTER = r"""
\end{tabular}
\end{document}
"""

def format_description(lines):
    latex = "\\begin{itemize}[leftmargin=*, noitemsep]\n"
    for line in lines:
        latex += f"\\item {line}\n"
    latex += "\\end{itemize}"
    return latex

def create_spell(spell):
    desc = format_description(spell["description"])
    return f"""
\\spell
{{{spell["color"]}}}
{{{spell["name"]}}}
{{{spell["level"]}}}
{{{spell["school"]}}}
{{{spell["casting_time"]}}}
{{{spell["range"]}}}
{{{spell["save"]}}}
{{{spell["duration"]}}}
{{{spell["components"]}}}
{{{desc}}}
{{{spell["higher_levels"]}}}
"""

with open("spells.json", "r", encoding="utf-8") as f:
    spells = json.load(f)

output = TEMPLATE_HEADER

for i, spell in enumerate(spells):
    output += create_spell(spell)

    if (i + 1) % 3 == 0:
        output += "\\\\\n"
    else:
        output += "&\n"

output += TEMPLATE_FOOTER

with open("cards.tex", "w", encoding="utf-8") as f:
    f.write(output)

print("cards.tex erfolgreich generiert!")