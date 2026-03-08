"""Interactive D3.js org chart component for Streamlit."""

from __future__ import annotations

import json

import streamlit as st

# ---------------------------------------------------------------------------
# Entity-type colour palette
# ---------------------------------------------------------------------------
ENTITY_COLORS = {
    "corporation": "#4e79a7",
    "llc": "#59a14f",
    "lp": "#e15759",
    "llp": "#e15759",
    "limited_company": "#76b7b2",
    "nonprofit": "#af7aa1",
    "other": "#9c755f",
    "portfolio": "#9c755f",
}

DEFAULT_COLOR = "#9c755f"


def _color_for(entity_type: str) -> str:
    return ENTITY_COLORS.get((entity_type or "").lower(), DEFAULT_COLOR)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_org_chart(tree_data: dict | list, height: int = 700) -> None:
    """Render an interactive D3 org chart inside the Streamlit app.

    Parameters
    ----------
    tree_data:
        Hierarchical data in D3-compatible format.  May be a single dict
        (one root) or a list (first element is used as root).
    height:
        Pixel height of the embedded component.
    """
    if isinstance(tree_data, list):
        if not tree_data:
            return
        tree_data = tree_data[0]

    if not tree_data:
        return

    data_json = json.dumps(tree_data, default=str)

    html = _build_html(data_json, height)
    st.components.v1.html(html, height=height, scrolling=False)


# ---------------------------------------------------------------------------
# HTML / JS / CSS builder
# ---------------------------------------------------------------------------

def _build_html(data_json: str, height: int) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
*, *::before, *::after {{ box-sizing: border-box; }}
html, body {{
  margin: 0; padding: 0; width: 100%; height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
               Helvetica, Arial, sans-serif;
  background: #f8f9fb; overflow: hidden;
}}
svg {{ width: 100%; height: 100%; cursor: grab; }}
svg:active {{ cursor: grabbing; }}

.node rect {{
  stroke-width: 1.6px; rx: 8; ry: 8;
  filter: drop-shadow(0 1px 3px rgba(0,0,0,.12));
  cursor: pointer;
}}
.node text {{
  font-size: 12px; fill: #fff; pointer-events: none; font-weight: 500;
}}
.node .standing-icon {{
  font-size: 11px; pointer-events: none;
}}
.link {{
  fill: none; stroke: #b0b8c4; stroke-width: 1.4px;
}}
.link-label {{
  font-size: 10px; fill: #6b7280; pointer-events: none;
  font-weight: 600;
}}
.tooltip {{
  position: absolute; padding: 10px 14px;
  background: #1f2937; color: #f3f4f6;
  border-radius: 6px; font-size: 12px; line-height: 1.55;
  pointer-events: none; opacity: 0;
  transition: opacity .15s ease;
  box-shadow: 0 4px 12px rgba(0,0,0,.2);
  max-width: 280px; z-index: 999;
}}
.tooltip .lbl {{ color: #9ca3af; margin-right: 4px; }}
</style>
</head>
<body>
<div id="chart"></div>
<div class="tooltip" id="tip"></div>
<script>
(function() {{
  "use strict";

  /* ---------- data ---------- */
  const rawData = {data_json};

  /* ---------- colour map ---------- */
  const COLORS = {{
    corporation: "#4e79a7", llc: "#59a14f",
    lp: "#e15759", llp: "#e15759",
    limited_company: "#76b7b2", nonprofit: "#af7aa1",
    other: "#9c755f", portfolio: "#9c755f"
  }};
  const colorOf = t => COLORS[(t || "").toLowerCase()] || "#9c755f";

  /* ---------- dimensions ---------- */
  const WIDTH  = document.body.clientWidth;
  const HEIGHT = {height};
  const NODE_W = 174, NODE_H = 50;
  const LEVEL_GAP = 120;            // vertical gap between levels

  /* ---------- SVG ---------- */
  const svg = d3.select("#chart")
    .append("svg").attr("width", WIDTH).attr("height", HEIGHT);
  const g = svg.append("g");

  /* ---------- zoom ---------- */
  const zoomBehavior = d3.zoom()
    .scaleExtent([0.1, 3])
    .on("zoom", e => g.attr("transform", e.transform));
  svg.call(zoomBehavior);

  /* ---------- tooltip ---------- */
  const tip = d3.select("#tip");
  function showTip(ev, d) {{
    const o = d.data;
    const pct = o.ownership_percentage != null ? o.ownership_percentage + "%" : "N/A";
    const gs = o.good_standing === true
      ? '<span style="color:#34d399">In Good Standing</span>'
      : o.good_standing === false
        ? '<span style="color:#f87171">Not in Good Standing</span>'
        : '<span style="color:#9ca3af">Unknown</span>';
    tip.html(
      '<strong>' + (o.name || '') + '</strong><br>' +
      '<span class="lbl">Type:</span>' + (o.entity_type || 'N/A') + '<br>' +
      '<span class="lbl">Jurisdiction:</span>' + (o.jurisdiction || 'N/A') + '<br>' +
      '<span class="lbl">Ownership:</span>' + pct + '<br>' +
      '<span class="lbl">Standing:</span>' + gs
    ).style("opacity", 1)
     .style("left", (ev.pageX + 14) + "px")
     .style("top",  (ev.pageY - 12) + "px");
  }}
  function moveTip(ev) {{
    tip.style("left", (ev.pageX + 14) + "px")
       .style("top",  (ev.pageY - 12) + "px");
  }}
  function hideTip() {{ tip.style("opacity", 0); }}

  /* ---------- hierarchy ---------- */
  const root = d3.hierarchy(rawData);
  root.x0 = 0;
  root.y0 = 0;

  // Determine initial collapse state from _default_collapsed flag.
  // If the flag is absent, default to collapsing nodes deeper than level 2.
  function initCollapse(d, depth) {{
    if (!d.children) return;
    const flag = d.data._default_collapsed;
    if (flag === true) {{
      d._children = d.children;
      d.children = null;
    }} else if (flag === false) {{
      // keep expanded, recurse
      d.children.forEach(c => initCollapse(c, depth + 1));
    }} else {{
      // no flag: collapse level 3+
      if (depth >= 2) {{
        d._children = d.children;
        d.children = null;
      }} else {{
        d.children.forEach(c => initCollapse(c, depth + 1));
      }}
    }}
  }}
  initCollapse(root, 0);

  const treeLayout = d3.tree().nodeSize([NODE_W + 24, LEVEL_GAP]);

  /* ---------- path generator ---------- */
  // Cubic bezier from bottom of parent to top of child
  function linkPath(d) {{
    const sy = d.source.y + NODE_H / 2;
    const ty = d.target.y - NODE_H / 2;
    const my = (sy + ty) / 2;
    return "M" + d.source.x + "," + sy +
           "C" + d.source.x + "," + my +
           " " + d.target.x + "," + my +
           " " + d.target.x + "," + ty;
  }}

  /* ---------- draw / update ---------- */
  const duration = 380;
  let idSeq = 0;

  function update(source) {{
    treeLayout(root);
    const nodes = root.descendants();
    const links = root.links();

    // Force y from depth so vertical spacing is consistent
    nodes.forEach(d => {{ d.y = d.depth * LEVEL_GAP; }});

    /* --- nodes --- */
    const node = g.selectAll("g.node")
      .data(nodes, d => d.data._uid || (d.data._uid = ++idSeq));

    const nodeEnter = node.enter().append("g")
      .attr("class", "node")
      .attr("transform", "translate(" + (source.x0 || 0) + "," + (source.y0 || 0) + ")")
      .on("click", (ev, d) => {{
        if (d.children) {{
          d._children = d.children;
          d.children = null;
        }} else if (d._children) {{
          d.children = d._children;
          d._children = null;
        }}
        update(d);
      }})
      .on("mouseover", showTip)
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);

    // Rounded rectangle
    nodeEnter.append("rect")
      .attr("width", NODE_W).attr("height", NODE_H)
      .attr("x", -NODE_W / 2).attr("y", -NODE_H / 2)
      .attr("fill", d => colorOf(d.data.entity_type))
      .attr("stroke", d => d3.color(colorOf(d.data.entity_type)).darker(0.4));

    // Entity name (line 1)
    nodeEnter.append("text")
      .attr("dy", "-0.2em")
      .attr("text-anchor", "middle")
      .text(d => {{
        const n = d.data.name || "";
        return n.length > 24 ? n.slice(0, 22) + "\u2026" : n;
      }});

    // Good-standing icon + entity type (line 2)
    nodeEnter.append("text")
      .attr("class", "standing-icon")
      .attr("dy", "1.15em")
      .attr("text-anchor", "middle")
      .attr("fill", d =>
        d.data.good_standing === true  ? "#a7f3d0" :
        d.data.good_standing === false ? "#fca5a5" : "#d1d5db")
      .text(d => {{
        const icon = d.data.good_standing === true  ? "\u2714" :
                     d.data.good_standing === false ? "\u2718" : "\u2014";
        return icon + "  " + (d.data.entity_type || "").toUpperCase();
      }});

    // Collapse indicator (below node)
    nodeEnter.append("text")
      .attr("class", "collapse-ind")
      .attr("dy", NODE_H / 2 + 14)
      .attr("text-anchor", "middle")
      .attr("fill", "#6b7280").attr("font-size", "10px");

    // --- update (merge) ---
    const nodeUpdate = nodeEnter.merge(node);
    nodeUpdate.transition().duration(duration)
      .attr("transform", d => "translate(" + d.x + "," + d.y + ")");

    nodeUpdate.select(".collapse-ind")
      .text(d => d._children ? "+ " + d._children.length + " more" : "");

    // --- exit ---
    node.exit().transition().duration(duration)
      .attr("transform", "translate(" + (source.x || 0) + "," + (source.y || 0) + ")")
      .remove()
      .select("rect").attr("width", 0).attr("height", 0);

    /* --- links --- */
    const link = g.selectAll("path.link")
      .data(links, d => d.target.data._uid);

    const linkEnter = link.enter().insert("path", "g")
      .attr("class", "link")
      .attr("d", function() {{
        const o = {{ x: source.x0 || 0, y: source.y0 || 0 }};
        return linkPath({{ source: o, target: o }});
      }});

    linkEnter.merge(link).transition().duration(duration)
      .attr("d", linkPath);

    link.exit().transition().duration(duration)
      .attr("d", function() {{
        const o = {{ x: source.x || 0, y: source.y || 0 }};
        return linkPath({{ source: o, target: o }});
      }}).remove();

    /* --- ownership labels on links --- */
    const lbl = g.selectAll("text.link-label")
      .data(links, d => d.target.data._uid);

    const lblEnter = lbl.enter().append("text")
      .attr("class", "link-label")
      .attr("text-anchor", "middle");

    lblEnter.merge(lbl).transition().duration(duration)
      .attr("x", d => (d.source.x + d.target.x) / 2)
      .attr("y", d => {{
        const sy = d.source.y + NODE_H / 2;
        const ty = d.target.y - NODE_H / 2;
        return (sy + ty) / 2 - 4;
      }})
      .text(d => {{
        const p = d.target.data.ownership_percentage;
        return p != null ? p + "%" : "";
      }});

    lbl.exit().transition().duration(duration).style("opacity", 0).remove();

    /* --- stash positions for next transition --- */
    nodes.forEach(d => {{ d.x0 = d.x; d.y0 = d.y; }});
  }}

  update(root);

  // Centre the tree initially
  svg.call(zoomBehavior.transform,
    d3.zoomIdentity.translate(WIDTH / 2, 40));

  // Resize
  window.addEventListener("resize", () => {{
    svg.attr("width", document.body.clientWidth);
  }});
}})();
</script>
</body>
</html>"""
