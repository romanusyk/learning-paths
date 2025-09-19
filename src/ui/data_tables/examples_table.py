from __future__ import annotations

import html
import json
from pathlib import Path
from typing import List, Dict, Any, Iterable

import pandas as pd


def _escape_html_text(text: str) -> str:
    return html.escape(text or "", quote=False)


def _load_data(form_csv: Path, obstacles_eng_csv: Path, map_json: Path) -> pd.DataFrame:
    df = pd.read_csv(form_csv)
    eng = pd.read_csv(obstacles_eng_csv)
    with open(map_json, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    labels_by_id: Dict[int, List[str]] = {}
    for row in mapping:
        rid = int(row.get("respondent_id"))
        labels = [str(x).strip() for x in row.get("labels", []) if str(x).strip()]
        labels_by_id[rid] = labels

    base = (
        eng.merge(df[["respondent_id", "obstacles", "enjoyed_school_classes"]], on="respondent_id", how="left")
        .rename(columns={"obstacles": "obstacles_orig", "obstacles_eng": "obstacles_eng"})
    )

    # Attach labels
    base["labels"] = base["respondent_id"].map(lambda rid: labels_by_id.get(int(rid), []))

    # Classify school experience: negative (1-2), positive (4-5), neutral (3 or missing)
    def classify_school_experience(score):
        if pd.isna(score):
            return "unknown"
        score = float(score)
        if score <= 2:
            return "negative"
        elif score >= 4:
            return "positive"
        else:
            return "neutral"
    
    base["school_experience"] = base["enjoyed_school_classes"].map(classify_school_experience)

    # Keep only rows that actually have any text
    base = base.assign(
        obstacles_orig=lambda d: d["obstacles_orig"].fillna("").astype(str).str.strip(),
        obstacles_eng=lambda d: d["obstacles_eng"].fillna("").astype(str).str.strip(),
    )
    base = base.query("obstacles_orig != '' or obstacles_eng != ''")
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
        css_lines.append(
            f".tag-filter-btn.tag-{slug} {{ background-color: hsl({hue} {s}% {l}%); color: #fff; border: none; }}"
        )
        css_lines.append(
            f".tag-filter-btn.tag-{slug}.active {{ box-shadow: 0 0 0 2px rgba(0,0,0,0.15) inset; }}"
        )
    base_css = """
<style>
  .tag-filter-btn { cursor: pointer; margin: 0 6px 6px 0; padding: 6px 10px; border-radius: 18px; background: #eee; border: 1px solid #ddd; }
  .tag-filter-btn.active { outline: 2px solid #222; }
  .school-filter-btn { cursor: pointer; margin: 0 6px 6px 0; padding: 6px 10px; border-radius: 18px; background: #eee; border: 1px solid #ddd; }
  .school-filter-btn.active { outline: 2px solid #222; }
  .school-filter-btn[data-school="negative"] { background-color: #ffb3b3; color: #000; border: 1px solid #ff6666; }
  .school-filter-btn[data-school="positive"] { background-color: #b3ffb3; color: #000; border: 1px solid #66ff66; }
  .school-filter-btn[data-school="negative"].active { outline: 2px solid #cc0000; }
  .school-filter-btn[data-school="positive"].active { outline: 2px solid #009900; }
  .lang-toggle-btn { cursor: pointer; margin: 0 6px 6px 0; padding: 6px 10px; border-radius: 6px; border: 1px solid #bbb; background: #fafafa; }
  .lang-toggle-btn.active { background: #333; color: #fff; border-color: #333; }
  .tag-pill { display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 0.9em; margin: 2px 4px 2px 0; white-space: nowrap; }
  .toolbar { margin-bottom: 0.5rem; }
  .toolbar h4 { margin: 0 0 6px 0; }
</style>
"""
    return base_css + "<style>" + "\n".join(css_lines) + "</style>"


def _build_buttons_html(unique_labels: Iterable[str], label_counts: Dict[str, int], school_counts: Dict[str, int]) -> str:
    # Build obstacle filter buttons (All + one per label)
    labels_sorted = sorted(unique_labels, key=lambda l: label_counts.get(l, 0), reverse=True)
    obstacle_buttons = [
        '<button class="tag-filter-btn active" data-tag="">All <span class="count-all-tags" style="opacity:0.85"></span></button>'
    ]
    for label in labels_sorted:
        safe = html.escape(label)
        slug = _slugify(label)
        obstacle_buttons.append(
            f'<button class="tag-filter-btn tag-{slug}" data-tag="{safe}">{safe} <span class="count-tag-{slug}" style="opacity:0.85"></span></button>'
        )

    # Build school experience filter buttons
    school_buttons = [
        '<button class="school-filter-btn active" data-school="">All <span class="count-all" style="opacity:0.85"></span></button>',
        '<button class="school-filter-btn" data-school="negative">Negative <span class="count-negative" style="opacity:0.85"></span></button>',
        '<button class="school-filter-btn" data-school="positive">Positive <span class="count-positive" style="opacity:0.85"></span></button>'
    ]

    # Language toggle buttons
    lang_toggle = (
        '<div style="margin-top: 0.5rem; margin-bottom: 0.5rem;" class="toolbar">'
        '<strong>Text language:</strong> '
        '<button id="lang-original" class="lang-toggle-btn active" data-lang="orig">Original</button> '
        '<button id="lang-english" class="lang-toggle-btn" data-lang="en">English</button>'
        '</div>'
    )

    obstacle_toolbar = (
        '<div style="margin-bottom: 0.5rem;" class="toolbar">'
        '<strong>Filter by obstacle:</strong> ' + "\n".join(obstacle_buttons) +
        '</div>'
    )
    
    school_toolbar = (
        '<div style="margin-bottom: 0.5rem;" class="toolbar">'
        '<strong>Filter by school experience:</strong> ' + "\n".join(school_buttons) +
        '</div>'
    )
    
    return _build_palette_css(labels_sorted) + obstacle_toolbar + school_toolbar + lang_toggle


def _build_table_html(df: pd.DataFrame, table_id: str) -> str:
    # Build cells with both language variants; show original by default
    def cell_text(row: pd.Series) -> str:
        orig = _escape_html_text(row["obstacles_orig"]) or "&nbsp;"
        en = _escape_html_text(row["obstacles_eng"]) or "&nbsp;"
        return (
            '<span class="obst-text">'
            f'<span class="text-orig">{orig}</span>'
            f'<span class="text-en" style="display:none">{en}</span>'
            '</span>'
        )

    def cell_tags(row: pd.Series) -> str:
        labels = row["labels"] or []
        spans = []
        for lab in labels:
            slug = _slugify(lab)
            spans.append(f'<span class="tag-pill tag-{slug}">{html.escape(lab)}</span>')
        return "".join(spans) or "&nbsp;"

    # Build manually to add row-level data attributes for filtering
    rows_html: List[str] = []
    for _, row in df.iterrows():
        labels = [str(lab) for lab in (row.get("labels") or [])]
        tags_attr = "|".join(l.lower() for l in labels)
        school_exp = str(row.get("school_experience", ""))
        rows_html.append(
            "<tr data-tags=\"" + html.escape(tags_attr) + "\" data-school=\"" + html.escape(school_exp) + "\">"
            + "<td>" + cell_text(row) + "</td>"
            + "<td>" + cell_tags(row) + "</td>"
            + "</tr>"
        )

    table_html = (
        f"<table id=\"{table_id}\" class=\"obstacles-table\">"
        "<thead><tr><th>Text</th><th>Obstacles</th></tr></thead>"
        "<tbody>" + "".join(rows_html) + "</tbody>"
        "</table>"
    )
    extra_css = """
<style>
  table.obstacles-table { width: 100%; border-collapse: separate; border-spacing: 0; }
  table.obstacles-table thead th { text-align: left; border-bottom: 2px solid #ddd; padding: 8px; }
  table.obstacles-table td { vertical-align: top; padding: 8px; border-bottom: 1px solid #eee; }
  table.obstacles-table td:first-child { width: 70%; }
</style>
"""
    return extra_css + table_html


def _build_script(table_id: str, tags_column_index: int = 1) -> str:
    # Vanilla JS filtering and language toggle (no external libs)
    return rf"""
<script>
  document.addEventListener('DOMContentLoaded', function() {{
    var table = document.getElementById('{table_id}');
    if (!table) return;
    
    var currentTagFilter = '';
    var currentSchoolFilter = '';

    function updateCounters() {{
      var tagLower = (currentTagFilter || '').toLowerCase();
      var schoolLower = (currentSchoolFilter || '').toLowerCase();
      var rows = table.querySelectorAll('tbody tr');
      
      // Count rows for school experience (based on tag filter)
      var schoolCounts = {{ all: 0, negative: 0, positive: 0 }};
      // Count rows for tags (based on school filter)
      var tagCounts = {{}};
      
      rows.forEach(function(row) {{
        var tags = row.getAttribute('data-tags') || '';
        var school = row.getAttribute('data-school') || '';
        
        var tagMatch = !tagLower || tags.split('|').some(function(t) {{ return t.trim() === tagLower; }});
        var schoolMatch = !schoolLower || school === schoolLower;
        
        // Count school experience based on current tag filter
        if (tagMatch) {{
          schoolCounts.all++;
          if (school === 'negative') schoolCounts.negative++;
          if (school === 'positive') schoolCounts.positive++;
        }}
        
        // Count tags based on current school filter
        if (schoolMatch) {{
          if (tags) {{
            tags.split('|').forEach(function(tag) {{
              var t = (tag || '').trim();
              if (t) {{
                var slug = t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'tag';
                tagCounts[slug] = (tagCounts[slug] || 0) + 1;
              }}
            }});
          }}
        }}
      }});
      
      // Update school counter displays
      var countAll = document.querySelector('.count-all');
      if (countAll) countAll.textContent = schoolCounts.all > 0 ? '(' + schoolCounts.all + ')' : '';
      
      var countNeg = document.querySelector('.count-negative');
      if (countNeg) countNeg.textContent = '(' + schoolCounts.negative + ')';
      
      var countPos = document.querySelector('.count-positive');
      if (countPos) countPos.textContent = '(' + schoolCounts.positive + ')';
      
      // Update tag counter displays
      var countAllTags = document.querySelector('.count-all-tags');
      if (countAllTags) countAllTags.textContent = schoolCounts.all > 0 ? '(' + schoolCounts.all + ')' : '';
      
      
      
      // Update every tag counter element based on computed counts
      document.querySelectorAll('[class^="count-tag-"]').forEach(function(counter) {{
        var className = counter.className;
        var match = className.match(/count-tag-([^\s]+)/);
        if (match) {{
          var slug = match[1];
          var val = tagCounts[slug] || 0;
          counter.textContent = '(' + val + ')';
        }}
      }});
    }}

    function applyFilters() {{
      var tagLower = (currentTagFilter || '').toLowerCase();
      var schoolLower = (currentSchoolFilter || '').toLowerCase();
      var rows = table.querySelectorAll('tbody tr');
      
      rows.forEach(function(row) {{
        var tags = row.getAttribute('data-tags') || '';
        var school = row.getAttribute('data-school') || '';
        
        var tagMatch = !tagLower || tags.split('|').some(function(t) {{ return t.trim() === tagLower; }});
        var schoolMatch = !schoolLower || school === schoolLower;
        
        row.style.display = (tagMatch && schoolMatch) ? '' : 'none';
      }});
      
      updateCounters();
    }}

    document.addEventListener('click', function(e) {{
      var btn = e.target.closest('.tag-filter-btn');
      if (btn) {{
        document.querySelectorAll('.tag-filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
        btn.classList.add('active');
        currentTagFilter = btn.getAttribute('data-tag') || '';
        applyFilters();
        return;
      }}
      
      var schoolBtn = e.target.closest('.school-filter-btn');
      if (schoolBtn) {{
        document.querySelectorAll('.school-filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
        schoolBtn.classList.add('active');
        currentSchoolFilter = schoolBtn.getAttribute('data-school') || '';
        applyFilters();
        return;
      }}
    }});

    function setLang(lang) {{
      table.querySelectorAll('.obst-text .text-en').forEach(function(el) {{ el.style.display = (lang==='en') ? '' : 'none'; }});
      table.querySelectorAll('.obst-text .text-orig').forEach(function(el) {{ el.style.display = (lang==='en') ? 'none' : ''; }});
    }}

    document.addEventListener('click', function(e) {{
      if (e.target && e.target.id === 'lang-original') {{
        document.querySelectorAll('.lang-toggle-btn').forEach(function(b) {{ b.classList.remove('active'); }});
        e.target.classList.add('active');
        setLang('orig');
      }} else if (e.target && e.target.id === 'lang-english') {{
        document.querySelectorAll('.lang-toggle-btn').forEach(function(b) {{ b.classList.remove('active'); }});
        e.target.classList.add('active');
        setLang('en');
      }}
    }});

    // default states
    setLang('orig');
    applyFilters();
  }});
</script>
"""


def render_examples_block(
    *,
    table_id: str,
    form_csv: str | Path,
    obstacles_eng_csv: str | Path,
    map_json: str | Path,
) -> str:
    base = _load_data(Path(form_csv), Path(obstacles_eng_csv), Path(map_json))
    
    # counts per label
    counts: Dict[str, int] = {}
    for labs in base["labels"]:
        for lab in labs:
            counts[lab] = counts.get(lab, 0) + 1
    unique_labels = sorted(counts.keys(), key=lambda l: counts[l], reverse=True)
    
    # counts per school experience
    school_counts: Dict[str, int] = {}
    for school_exp in base["school_experience"]:
        school_counts[school_exp] = school_counts.get(school_exp, 0) + 1
    
    buttons_html = _build_buttons_html(unique_labels, counts, school_counts)
    table_html = _build_table_html(base, table_id)
    script_html = _build_script(table_id)
    return buttons_html + table_html + script_html
