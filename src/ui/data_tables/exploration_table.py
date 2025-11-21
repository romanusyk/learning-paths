from __future__ import annotations

import html
import json
from pathlib import Path
from typing import List, Dict, Any, Iterable

import pandas as pd


def _escape_html_text(text: str) -> str:
    return html.escape(text or "", quote=False)


def _load_data(form_csv: Path, obstacles_eng_csv: Path, extra_methods_eng_csv: Path, map_json: Path) -> pd.DataFrame:
    df = pd.read_csv(form_csv)
    obs_eng = pd.read_csv(obstacles_eng_csv)
    meth_eng = pd.read_csv(extra_methods_eng_csv)
    
    with open(map_json, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    labels_by_id: Dict[int, List[str]] = {}
    for row in mapping:
        rid = int(row.get("respondent_id"))
        labels = [str(x).strip() for x in row.get("labels", []) if str(x).strip()]
        labels_by_id[rid] = labels

    # Merge obstacles English translations
    base = df.merge(obs_eng[["respondent_id", "obstacles_eng"]], on="respondent_id", how="left")
    
    # Merge extra methods English translations
    base = base.merge(meth_eng[["respondent_id", "extra_methods_eng"]], on="respondent_id", how="left")

    # Attach labels
    base["obstacles_labels"] = base["respondent_id"].map(lambda rid: labels_by_id.get(int(rid), []))

    # Ensure string columns are strings
    base = base.assign(
        obstacles=lambda d: d["obstacles"].fillna("").astype(str).str.strip(),
        obstacles_eng=lambda d: d["obstacles_eng"].fillna("").astype(str).str.strip(),
        extra_methods=lambda d: d["extra_methods"].fillna("").astype(str).str.strip(),
        extra_methods_eng=lambda d: d["extra_methods_eng"].fillna("").astype(str).str.strip(),
    )
    
    return base


def _slugify(label: str) -> str:
    import re
    s = label.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "tag"


def _build_palette_css(unique_labels: List[str]) -> str:
    # Deterministic pleasant palette using HSL spaced around color wheel
    css_lines: List[str] = []
    n = max(1, len(unique_labels))
    for idx, label in enumerate(unique_labels):
        hue = int((360.0 * idx) / n)
        s = 70
        l = 42
        slug = _slugify(label)
        css_lines.append(
            f".tag-pill.tag-{slug} {{ background-color: hsl({hue} {s}% {l}%); color: #fff; }}"
        )
        
    base_css = """
<style>
  .lang-toggle-btn { cursor: pointer; margin: 0 6px 6px 0; padding: 6px 10px; border-radius: 6px; border: 1px solid #bbb; background: #fafafa; }
  .lang-toggle-btn.active { background: #333; color: #fff; border-color: #333; }
  .tag-pill { display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 0.9em; margin: 2px 4px 2px 0; white-space: nowrap; }
  .toolbar { margin-bottom: 0.5rem; }
</style>
"""
    return base_css + "<style>" + "\n".join(css_lines) + "</style>"


def _build_table_html(df: pd.DataFrame, table_id: str) -> str:
    def cell_text(orig: str, eng: str) -> str:
        orig = _escape_html_text(orig) or "&nbsp;"
        eng = _escape_html_text(eng) or "&nbsp;"
        return (
            '<span class="content-text">'
            f'<span class="text-orig">{orig}</span>'
            f'<span class="text-en" style="display:none">{eng}</span>'
            '</span>'
        )

    def cell_tags(labels: List[str]) -> str:
        spans = []
        for lab in labels:
            slug = _slugify(lab)
            spans.append(f'<span class="tag-pill tag-{slug}">{html.escape(lab)}</span>')
        return "".join(spans) or "&nbsp;"

    # Determine columns to display
    # We want all columns from df, but we need to handle obstacles and extra_methods specially
    # and insert obstacles_labels next to obstacles
    
    # Get original columns from form_data (excluding the added eng/labels columns)
    # We can assume the first N columns are from form_data, or just filter
    # But simpler is to take all columns except the ones we added for internal use if we want strictness
    # However, the requirement is "all columns from raw data".
    
    # Let's construct the list of columns to show
    cols_to_show = []
    
    # Identify columns that are NOT the auxiliary ones we added
    aux_cols = {"obstacles_eng", "extra_methods_eng", "obstacles_labels"}
    
    # We want to preserve the order of the original csv if possible.
    # df.columns contains all columns now.
    
    for col in df.columns:
        if col in aux_cols:
            continue
            
        cols_to_show.append(col)
        
        # Insert labels after obstacles
        if col == "obstacles":
            cols_to_show.append("obstacles_labels")

    # Build header HTML
    header_cells = []
    for col in cols_to_show:
        header_name = col.replace("_", " ").title()
        if col == "obstacles_labels":
            header_name = "Obstacle Labels"
        header_cells.append(f"<th>{html.escape(header_name)}</th>")
    
    thead_html = "<thead><tr>" + "".join(header_cells) + "</tr></thead>"

    # Build body HTML
    rows_html: List[str] = []
    for _, row in df.iterrows():
        cells = []
        for col in cols_to_show:
            val = row[col]
            
            if col == "obstacles":
                # Rich text column
                content = cell_text(str(val), str(row.get("obstacles_eng", "")))
                cells.append(f"<td class='col-obstacles'>{content}</td>")
            elif col == "extra_methods":
                # Rich text column
                content = cell_text(str(val), str(row.get("extra_methods_eng", "")))
                cells.append(f"<td class='col-methods'>{content}</td>")
            elif col == "obstacles_labels":
                # Tags column
                content = cell_tags(val if isinstance(val, list) else [])
                cells.append(f"<td class='col-tags'>{content}</td>")
            else:
                # Normal column
                content = html.escape(str(val)) if pd.notna(val) else ""
                cells.append(f"<td>{content}</td>")
        
        rows_html.append("<tr>" + "".join(cells) + "</tr>")

    table_html = (
        f"<table id=\"{table_id}\" class=\"exploration-table\">"
        f"{thead_html}"
        "<tbody>" + "".join(rows_html) + "</tbody>"
        "</table>"
    )
    
    # Updated CSS for wide table
    extra_css = """
<style>
  table.exploration-table { 
    border-collapse: separate; 
    border-spacing: 0; 
    width: max-content; /* Force table to take necessary width */
    min-width: 100%;
    font-size: 0.9rem;
  }
  table.exploration-table thead th { 
    text-align: left; 
    border-bottom: 2px solid #ddd; 
    padding: 8px; 
    background: #f9f9f9;
    white-space: nowrap;
    position: sticky;
    top: 0;
    z-index: 10;
  }
  table.exploration-table td { 
    vertical-align: top; 
    padding: 8px; 
    border-bottom: 1px solid #eee; 
    white-space: nowrap; /* Force single line for data density */
    max-width: 400px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  /* Allow wrapping for the long text columns if needed, or keep them truncated with hover? 
     Let's allow wrapping for the main text columns but with a min-width */
  table.exploration-table td.col-obstacles { 
    min-width: 300px; 
    white-space: normal; 
  }
  table.exploration-table td.col-methods { 
    min-width: 250px; 
    white-space: normal; 
  }
  table.exploration-table td.col-tags { 
    min-width: 200px; 
    white-space: normal; 
  }
  
</style>
"""
    return extra_css + f"<div class='table-container'>{table_html}</div>"


def _build_script(table_id: str) -> str:
    return rf"""
<script>
  document.addEventListener('DOMContentLoaded', function() {{
    var table = document.getElementById('{table_id}');
    if (!table) return;

    function setLang(lang) {{
      table.querySelectorAll('.content-text .text-en').forEach(function(el) {{ el.style.display = (lang==='en') ? '' : 'none'; }});
      table.querySelectorAll('.content-text .text-orig').forEach(function(el) {{ el.style.display = (lang==='en') ? 'none' : ''; }});
    }}

    document.addEventListener('click', function(e) {{
      if (e.target && e.target.id === 'lang-original-exp') {{
        document.querySelectorAll('.lang-toggle-btn').forEach(function(b) {{ b.classList.remove('active'); }});
        e.target.classList.add('active');
        setLang('orig');
      }} else if (e.target && e.target.id === 'lang-english-exp') {{
        document.querySelectorAll('.lang-toggle-btn').forEach(function(b) {{ b.classList.remove('active'); }});
        e.target.classList.add('active');
        setLang('en');
      }}
    }});

    // default state
    setLang('orig');
  }});
</script>
"""


def render_exploration_table(
    *,
    table_id: str,
    form_csv: str | Path,
    obstacles_eng_csv: str | Path,
    extra_methods_eng_csv: str | Path,
    map_json: str | Path,
) -> str:
    base = _load_data(Path(form_csv), Path(obstacles_eng_csv), Path(extra_methods_eng_csv), Path(map_json))
    
    # Collect unique labels for palette generation
    all_labels = set()
    for labs in base["obstacles_labels"]:
        all_labels.update(labs)
    unique_labels = sorted(list(all_labels))
    
    palette_css = _build_palette_css(unique_labels)
    
    lang_toggle = (
        '<div style="margin-top: 0.5rem; margin-bottom: 0.5rem;" class="toolbar">'
        '<strong>Text language:</strong> '
        '<button id="lang-original-exp" class="lang-toggle-btn active" data-lang="orig">Original</button> '
        '<button id="lang-english-exp" class="lang-toggle-btn" data-lang="en">English</button>'
        '</div>'
    )
    
    table_html = _build_table_html(base, table_id)
    script_html = _build_script(table_id)
    
    return palette_css + lang_toggle + table_html + script_html
