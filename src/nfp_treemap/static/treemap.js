/* Bancreek U.S. Employment Data Treemap.
   PAYLOAD is injected by build.py as a global before this script runs. */
(() => {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";
  const $ = (sel) => document.querySelector(sel);

  // NBER recession peaks -> troughs, monthly. Shaded on the tooltip sparkline:
  // in an employment series almost every sharp drop is one of these, so without
  // them a reader has no way to separate a downturn from an industry story.
  const RECESSIONS = [
    ["1948-11", "1949-10"], ["1953-07", "1954-05"], ["1957-08", "1958-04"],
    ["1960-04", "1961-02"], ["1969-12", "1970-11"], ["1973-11", "1975-03"],
    ["1980-01", "1980-07"], ["1981-07", "1982-11"], ["1990-07", "1991-03"],
    ["2001-03", "2001-11"], ["2007-12", "2009-06"], ["2020-02", "2020-04"],
  ];

  // ---------------------------------------------------------------- decode
  // Values arrive delta-encoded at 10x (CES publishes thousands to 1dp).
  const byCode = new Map();
  for (const item of PAYLOAD.industries) {
    const vals = new Float64Array(item.d.length);
    let acc = 0;
    for (let i = 0; i < item.d.length; i++) {
      acc += item.d[i];
      vals[i] = acc / 10;
    }
    item.vals = vals;
    item.d = null;
    byCode.set(item.c, item);
  }

  // Ancestor chain per industry, root-first, used for drill filtering.
  for (const item of PAYLOAD.industries) {
    const chain = [];
    let cur = item;
    const guard = new Set();
    while (cur && !guard.has(cur.c)) {
      guard.add(cur.c);
      chain.unshift(cur.c);
      cur = cur.p ? byCode.get(cur.p) : null;
    }
    item.chain = chain;
  }

  const LEVELS = [...new Set(PAYLOAD.industries.map((i) => i.l))].sort((a, b) => a - b);
  const PERIOD_START = PAYLOAD.periodStart;
  const LABELS = PAYLOAD.periodLabels;
  const ANOM = PAYLOAD.anomaly;
  const HORIZONS = PAYLOAD.horizons;
  const labelToIdx = new Map(LABELS.map((l, i) => [l, i + PERIOD_START]));

  const valueAt = (item, idx) => {
    const off = idx - item.s;
    return off >= 0 && off < item.vals.length ? item.vals[off] : null;
  };

  // ---------------------------------------------------------------- metrics
  function change(item, idx, h, metric) {
    const now = valueAt(item, idx);
    const then = valueAt(item, idx - h);
    if (now === null || then === null) return null;
    if (metric === "pct") return then === 0 ? null : ((now - then) / Math.abs(then)) * 100;
    return now - then;
  }

  const median = (sorted) => {
    const n = sorted.length;
    return n % 2 ? sorted[(n - 1) / 2] : (sorted[n / 2 - 1] + sorted[n / 2]) / 2;
  };

  /* Score the current change against the same industry's own history of
     same-length changes. Four corrections, each forced by a wrong answer the
     simpler version actually produced:

     1. Robust z - median and MAD, not mean and SD. One 2020 tail inflates the
        SD enough to hide a real move: Food Services scored a "typical" -0.81
        while sitting at the 5th percentile of its own history.

     2. The whole 2020-22 distortion is excluded, not just the acute collapse,
        and a window is dropped if EITHER endpoint falls inside it. A 3-year
        window starting September 2020 still measures from deep in the hole.

     3. The lookback scales with the horizon and has a 20-year floor, so the
        reference distribution spans at least one business cycle. A fixed
        10-year window holds ~3 independent 3-year windows, and once the
        pandemic is excluded it contains no downturn at all - which is how an
        ordinary +403k year scored z = -4.05, "extreme".

     4. Overlapping windows are not independent. Below 6 non-overlapping ones
        it reports insufficient history instead of a confident wrong number.

     0.6745 rescales MAD so the result is comparable to a classical z under
     normality (MAD ~= 0.6745 * sigma). */
  const distorted = (t) => t >= ANOM.distortedStart && t <= ANOM.distortedEnd;
  const scored = (stat) => !!stat && !stat.insufficient && !stat.spansDisruption;

  function anomaly(item, idx, h, metric) {
    const current = change(item, idx, h, metric);
    if (current === null) return null;

    // Scoring a window that itself straddles the pandemic against windows that
    // do not is meaningless; say so rather than print a number.
    if (distorted(idx) || distorted(idx - h)) {
      return { current, spansDisruption: true };
    }

    const lookback = Math.max(ANOM.lookbackFloor, ANOM.lookbackPerHorizon * h);
    const samples = [];
    let earliest = null;
    for (let t = idx - lookback; t <= idx; t++) {
      // Either endpoint inside the distorted span disqualifies the sample.
      if (distorted(t) || distorted(t - h)) continue;
      const v = change(item, t, h, metric);
      if (v === null) continue;
      if (earliest === null) earliest = t - h;
      samples.push(v);
    }
    // The requested lookback is often longer than the series itself - a 10-year
    // horizon asks for 100 years and Total nonfarm only starts in 1939. Report
    // the span actually covered so the tooltip cannot overclaim.
    const spanMonths = earliest === null ? 0 : idx - earliest;

    // Overlapping windows are not independent observations: n/h of them are.
    const independent = samples.length / h;
    if (samples.length < ANOM.minSamples || independent < ANOM.minIndependent) {
      return {
        current, insufficient: true, n: samples.length,
        independent, lookback, spanMonths,
      };
    }

    const sorted = [...samples].sort((a, b) => a - b);
    const med = median(sorted);
    const mad = median([...samples].map((v) => Math.abs(v - med)).sort((a, b) => a - b));
    if (!(mad > 0)) {
      return {
        current, insufficient: true, n: samples.length,
        independent, lookback, spanMonths,
      };
    }

    const z = (0.6745 * (current - med)) / mad;
    const below = sorted.filter((v) => v < current).length;
    const pct = (below / sorted.length) * 100;
    const a = Math.abs(z);
    const label = a < 1 ? "typical" : a < 2 ? "notable" : a < 3 ? "unusual" : "extreme";
    return {
      current, median: med, mad, z, pct, label,
      n: samples.length, independent, lookback, spanMonths,
    };
  }

  // ---------------------------------------------------------------- palette
  const RAMPS = {
    accessible: {
      loss: ["--loss-1", "--loss-2", "--loss-3", "--loss-4", "--loss-5", "--loss-6"],
      gain: ["--gain-1", "--gain-2", "--gain-3", "--gain-4", "--gain-5", "--gain-6"],
      mid: "--div-mid",
    },
  };
  // The Tableau original's red-yellow-green. Kept as an option for continuity,
  // not the default: its poles measure CVD dE 5.1 (target >= 8), so under
  // deuteranopia gains and losses collapse toward the same olive.
  const CLASSIC = {
    loss: ["#fee08b", "#fdae61", "#f46d43", "#d73027", "#a50026", "#6d0019"],
    gain: ["#d9ef8b", "#a6d96a", "#66bd63", "#1a9850", "#00702f", "#00441f"],
    mid: "#ffffbf",
  };

  const cssVar = (name) =>
    getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  function ramp() {
    if (state.palette === "classic") return CLASSIC;
    const r = RAMPS.accessible;
    return {
      loss: r.loss.map(cssVar),
      gain: r.gain.map(cssVar),
      mid: cssVar(r.mid),
    };
  }

  /* Colour is symmetric around zero. Scaling across the raw min..max - as the
     Tableau version does - puts zero off the midpoint, so a -20k loss and a
     +20k gain render at different intensities and the eye reads a bias that
     is not in the data. */
  /* "No data" gets a hatch, not a flat grey. A flat grey sits a hair away from
     the neutral midpoint - especially in dark mode, where #2c2c2a and #383835
     are indistinguishable - so a missing observation reads as a real zero
     change, which is a different and much more interesting claim. */
  function ensureHatch() {
    if (svg.querySelector("#nodata-hatch")) return;
    const defs = document.createElementNS(SVG_NS, "defs");
    defs.innerHTML =
      `<pattern id="nodata-hatch" patternUnits="userSpaceOnUse" width="6" height="6" ` +
      `patternTransform="rotate(45)">` +
      `<rect width="6" height="6" fill="${cssVar("--nodata")}"/>` +
      `<line x1="0" y1="0" x2="0" y2="6" stroke="${cssVar("--muted")}" stroke-width="2"/>` +
      `</pattern>`;
    svg.appendChild(defs);
  }

  function colorFor(value, maxAbs, pal) {
    if (value === null) return "url(#nodata-hatch)";
    if (maxAbs <= 0) return pal.mid;
    const t = Math.min(1, Math.abs(value) / maxAbs);
    if (t < 0.02) return pal.mid;
    const arm = value < 0 ? pal.loss : pal.gain;
    return arm[Math.min(arm.length - 1, Math.floor(t * arm.length))];
  }

  // ---------------------------------------------------------------- layout
  /* Squarified treemap (Bruls, Huizing & van Wijk 2000). Rolled by hand rather
     than pulling in d3-hierarchy: the only piece needed is this function, and
     the payload is already 1.8 MB. */
  function squarify(nodes, x, y, w, h) {
    const out = [];
    const items = nodes.filter((n) => n.value > 0).sort((a, b) => b.value - a.value);
    if (!items.length || w <= 0 || h <= 0) return out;

    const total = items.reduce((s, n) => s + n.value, 0);
    const scale = (w * h) / total;
    const areas = items.map((n) => n.value * scale);

    const worst = (row, sum, side) => {
      const s2 = sum * sum;
      const side2 = side * side;
      let mx = -Infinity;
      let mn = Infinity;
      for (const a of row) { if (a > mx) mx = a; if (a < mn) mn = a; }
      return Math.max((side2 * mx) / s2, s2 / (side2 * mn));
    };

    let i = 0;
    let cx = x, cy = y, cw = w, ch = h;
    while (i < areas.length) {
      const side = Math.min(cw, ch);
      const row = [];
      let sum = 0;
      let best = Infinity;
      let j = i;
      while (j < areas.length) {
        const next = sum + areas[j];
        const r = worst([...row, areas[j]], next, side);
        if (row.length && r > best) break;
        row.push(areas[j]);
        sum = next;
        best = r;
        j++;
      }
      const horizontal = cw >= ch;
      const thickness = horizontal ? sum / ch : sum / cw;
      let offset = horizontal ? cy : cx;
      for (let k = 0; k < row.length; k++) {
        const extent = horizontal ? row[k] / thickness : row[k] / thickness;
        out.push({
          node: items[i + k],
          x: horizontal ? cx : offset,
          y: horizontal ? offset : cy,
          w: horizontal ? thickness : extent,
          h: horizontal ? extent : thickness,
        });
        offset += extent;
      }
      if (horizontal) { cx += thickness; cw -= thickness; }
      else { cy += thickness; ch -= thickness; }
      i = j;
    }
    return out;
  }

  // ---------------------------------------------------------------- text fit
  const measureCtx = document.createElement("canvas").getContext("2d");
  const FONT_STACK = 'system-ui, -apple-system, "Segoe UI", sans-serif';

  /* letterSpacing must be passed explicitly: canvas measureText ignores it, so
     a label styled with letter-spacing renders wider than it measures and gets
     clipped mid-word. Callers must also pass text already transformed to its
     rendered case - measuring "Professional and business services" and then
     letting CSS render it uppercase understates the width badly. */
  function textWidth(text, size, weight = 400, letterSpacing = 0) {
    measureCtx.font = `${weight} ${size}px ${FONT_STACK}`;
    return measureCtx.measureText(text).width + letterSpacing * size * text.length;
  }

  /* Wrap to whole words only. If even the first word will not fit, return null
     so the caller drops the label entirely - the Tableau version clips
     mid-word ("Repair and", "Support activities for"), which reads as a
     different industry name than the one actually there. */
  function wrapText(text, maxWidth, size, maxLines, weight, letterSpacing = 0) {
    const words = text.split(/\s+/);
    if (textWidth(words[0], size, weight, letterSpacing) > maxWidth) return null;
    const lines = [];
    let line = words[0];
    for (let i = 1; i < words.length; i++) {
      const candidate = `${line} ${words[i]}`;
      if (textWidth(candidate, size, weight, letterSpacing) <= maxWidth) {
        line = candidate;
      } else {
        lines.push(line);
        if (lines.length === maxLines) return { lines, truncated: true };
        line = words[i];
        if (textWidth(line, size, weight, letterSpacing) > maxWidth) {
          return { lines, truncated: true };
        }
      }
    }
    lines.push(line);
    return { lines, truncated: false };
  }

  // ---------------------------------------------------------------- format
  const fmtAbs = (v) => {
    if (v === null) return "n/a";
    const s = v < 0 ? "-" : "+";
    const a = Math.abs(v);
    return `${s}${a >= 1000 ? (a / 1000).toFixed(2) + "M" : a.toFixed(2) + "k"}`;
  };
  const fmtPct = (v) => (v === null ? "n/a" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`);
  const fmtValue = (v, metric) => (metric === "pct" ? fmtPct(v) : fmtAbs(v));
  const fmtLevel = (v) =>
    v === null ? "n/a" : `${(v / 1000).toFixed(3).replace(/\.?0+$/, "")}M`;
  const prettyMonth = (label) => {
    const [y, m] = label.split("-");
    return `${["January","February","March","April","May","June","July","August","September","October","November","December"][+m - 1]} ${y}`;
  };

  // ---------------------------------------------------------------- state
  /* A framed page is sized by its parent, so it drops the masthead and gives
     the chart the room instead. Auto-detected, but `#embed=0` / `#embed=1`
     overrides it — a host that wants the full layout inside an iframe (or the
     compact one standalone) can say so in the URL. */
  const EMBEDDED = (() => {
    const flag = new URLSearchParams(location.hash.slice(1)).get("embed");
    if (flag === "0") return false;
    if (flag === "1") return true;
    try { return window.self !== window.top; } catch { return true; }
  })();
  if (EMBEDDED) {
    document.documentElement.classList.add("embed");
    // The masthead is hidden when embedded, but the branding should still
    // travel with the chart, so move the single logo down to the footer.
    const brand = $("#brand");
    const footer = $("#footer-brand");
    if (brand && footer) footer.insertBefore(brand, footer.firstChild);
  }

  /* Measure the element, not the window. Inside the Prismic oEmbed the
     viewport does not describe the space the page is actually given, which is
     the same reason the CSS uses container queries. */
  const containerWidth = () => {
    const box = document.querySelector(".wrap");
    return Math.round(box?.getBoundingClientRect().width || innerWidth || 900);
  };
  const viewportHeight = () =>
    document.documentElement.clientHeight || innerHeight || 0;
  /* Theme follows the viewer's OS setting by default, which is right for a
     standalone page and wrong for an embed: a dark-mode visitor would get a
     dark chart inside a light article. `#theme=light` / `#theme=dark` pins it;
     the CSS already honours data-theme in both directions. */
  (() => {
    const pin = new URLSearchParams(location.hash.slice(1)).get("theme");
    if (pin === "light" || pin === "dark") {
      document.documentElement.dataset.theme = pin;
    } else if (EMBEDDED) {
      // Embedded, the host page's theme governs, and we cannot read it. The
      // host is light, so default to light rather than letting a dark-mode
      // visitor get a dark chart inside a light article. #theme=dark overrides.
      document.documentElement.dataset.theme = "light";
    }
  })();

  const NARROW = () => containerWidth() < 620;

  const state = {
    base: PAYLOAD.defaultBase || LABELS[LABELS.length - 1],
    horizon: "1mo",
    // Open at level 3 (the sectors), shallower still on a phone where even
    // that many tiles get unreadable. An explicit level in the URL still wins.
    level: NARROW() ? 2 : 3,
    metric: "abs",
    palette: "accessible",
    drill: null,
    highlight: "",
    showDupes: false,
    theme: null,          // null = follow the viewer's OS setting
  };

  function readHash() {
    const h = new URLSearchParams(location.hash.slice(1));
    if (h.has("base") && labelToIdx.has(h.get("base"))) state.base = h.get("base");
    if (h.has("h") && HORIZONS[h.get("h")]) state.horizon = h.get("h");
    if (h.has("lvl") && LEVELS.includes(+h.get("lvl"))) state.level = +h.get("lvl");
    if (h.has("m")) state.metric = h.get("m") === "pct" ? "pct" : "abs";
    if (h.has("pal")) state.palette = h.get("pal") === "classic" ? "classic" : "accessible";
    if (h.has("drill") && byCode.has(h.get("drill"))) state.drill = h.get("drill");
    if (h.has("q")) state.highlight = h.get("q");
    if (h.get("dupes") === "1") state.showDupes = true;
    const theme = h.get("theme");
    if (theme === "light" || theme === "dark") state.theme = theme;
  }

  function writeHash() {
    const p = new URLSearchParams({
      base: state.base, h: state.horizon, lvl: String(state.level),
      m: state.metric, pal: state.palette,
    });
    if (state.drill) p.set("drill", state.drill);
    if (state.highlight) p.set("q", state.highlight);
    if (state.showDupes) p.set("dupes", "1");
    if (state.theme) p.set("theme", state.theme);
    history.replaceState(null, "", `#${p}`);
  }

  // ---------------------------------------------------------------- selection
  function currentRows() {
    const idx = labelToIdx.get(state.base);
    const h = HORIZONS[state.horizon];
    const drill = state.drill;
    const rows = [];
    for (const item of PAYLOAD.industries) {
      if (item.l !== state.level) continue;
      // CES publishes a few roll-ups at the SAME level as the components they
      // contain, so showing both double-counts: at level 4 "Health care" is
      // exactly Ambulatory + Hospitals + Nursing, and including it made the
      // Health care and social assistance children sum to 61.3k against a true
      // 41.0k. Hidden unless explicitly asked for.
      if (item.dup && !state.showDupes) continue;
      if (drill && (item.c === drill || !item.chain.includes(drill))) continue;
      rows.push({ item, value: change(item, idx, h, state.metric) });
    }
    return rows;
  }

  const hasChildren = (code) => {
    const parent = byCode.get(code);
    if (!parent) return false;
    return PAYLOAD.industries.some(
      (i) => i.l > parent.l && i.chain.includes(code) && i.c !== code
    );
  };

  function groupOf(item) {
    if (!state.drill) return { code: item.ss, name: item.ssn };
    const parent = byCode.get(state.drill);
    const pos = item.chain.indexOf(state.drill);
    const childCode = item.chain[pos + 1];
    const child = byCode.get(childCode);
    return child && child.c !== item.c
      ? { code: child.c, name: child.n }
      : { code: parent.c, name: parent.n };
  }

  // ---------------------------------------------------------------- render
  const svg = $("#treemap");
  const GROUP_LABEL_H = 17;

  function render() {
    writeHash();
    syncControls();

    const rows = currentRows();
    const pal = ramp();
    svg.textContent = "";

    const withData = rows.filter((r) => r.value !== null);
    if (!rows.length) {
      $("#empty").hidden = false;
      $("#empty").textContent = "No industries at this level under the current selection.";
      svg.setAttribute("viewBox", "0 0 100 1");
      updateChrome(0);
      // Must still run: returning early here left the previous view's notes
      // on screen, describing industries that are no longer displayed.
      updateLagNote(rows);
      updateLevelNote(rows);
      $("#nomatch").hidden = true;
      return;
    }
    $("#empty").hidden = true;

    const maxAbs = withData.length ? Math.max(...withData.map((r) => Math.abs(r.value))) : 0;

    // Group by supersector (top level) or by the drill node's direct children.
    const groups = new Map();
    for (const row of rows) {
      const g = groupOf(row.item);
      if (!groups.has(g.code)) groups.set(g.code, { ...g, rows: [], value: 0 });
      const bucket = groups.get(g.code);
      bucket.rows.push(row);
      bucket.value += Math.abs(row.value ?? 0);
    }

    // The notes sit above the chart, so they must be in the DOM before the
    // embedded height is measured: on release day the "awaiting publication"
    // note is visible at the default view, and sizing the chart first pushed
    // it 30px past the bottom of a fixed-height iframe.
    updateLagNote(rows);
    updateLevelNote(rows);
    // Dimming every tile because the query matched nothing just looks broken;
    // fall back to no highlighting and say so.
    let q = state.highlight.trim().toLowerCase();
    const matches = q ? rows.filter((r) => r.item.n.toLowerCase().includes(q)).length : 0;
    $("#nomatch").hidden = !(q && matches === 0);
    $("#nomatch").textContent = `No industry at level ${state.level} matches “${state.highlight}”.`;
    if (q && matches === 0) q = "";

    const width = Math.max(280, svg.clientWidth || svg.parentElement.clientWidth - 16);
    // A handful of tiles stretched over a full-height canvas looks broken;
    // shrink the canvas rather than inflate four rectangles to 760px tall.
    // A single tile (level 0 = Total nonfarm) carries no area information, so
    // it reads as a banner rather than a chart; don't give it a full canvas.
    const cap = rows.length === 1 ? 170
      : rows.length <= 3 ? 300
      : rows.length <= 6 ? 380
      : rows.length <= 14 ? 520 : 760;
    // On a narrow screen the width is the binding constraint, so a 0.46 ratio
    // leaves tiles too small to label; go taller than wide instead. Embedded,
    // the parent's height governs, so the tall-phone ratio does not apply.
    const ratio = !EMBEDDED && containerWidth() < 620 ? 1.15 : 0.46;
    // cap last: a floor applied after it would override the small-count caps.
    let height = Math.min(cap, Math.max(300, Math.round(width * ratio)));

    // Embedded, the parent dictates the height: fit the chart to what is left
    // rather than overflow the iframe and hand the reader a scrollbar.
    if (EMBEDDED) {
      const top = svg.parentElement.getBoundingClientRect().top;
      // offsetHeight is 0 before the first paint; the fallback must cover the
      // real legend block (caption + bar + ends + no-data key), or the last
      // line gets clipped by the iframe on the very first render.
      const legend = $(".legend-row")?.offsetHeight || 0;
      // Slack covers the provenance stamp, which wraps below the legend at
      // narrower embed widths and would otherwise be cut off.
      const below = (legend > 20 ? legend : 108) + 42;
      /* Fill the height the host allocated, don't just avoid overflowing it.
         Clamping to min(natural, available) left ~450px blank in an 879x1200
         embed. With many tiles the chart takes whatever is left; with only a
         few, the small-count caps still apply so four rectangles are not
         stretched over 900px. 140px is the floor below which a treemap stops
         being readable, and the frame is allowed to scroll instead. */
      const available = Math.round(viewportHeight() - top - below);
      const ceiling = rows.length > 14 ? available : Math.min(cap, available);
      height = Math.max(140, Math.min(ceiling, available));
    }
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("height", height);
    ensureHatch();

    const groupList = [...groups.values()].filter((g) => g.value > 0);
    // A group whose members are all exactly zero still deserves a slot.
    const zeroGroups = [...groups.values()].filter((g) => g.value <= 0);
    for (const g of zeroGroups) { g.value = 1e-9; groupList.push(g); }

    const placed = squarify(groupList, 0, 0, width, height);

    for (const cell of placed) {
      const group = cell.node;
      const g = document.createElementNS(SVG_NS, "g");

      const frame = document.createElementNS(SVG_NS, "rect");
      frame.setAttribute("class", "groupframe");
      frame.setAttribute("x", cell.x + 1); frame.setAttribute("y", cell.y + 1);
      frame.setAttribute("width", Math.max(0, cell.w - 2));
      frame.setAttribute("height", Math.max(0, cell.h - 2));
      g.appendChild(frame);

      // Uppercased here rather than by CSS so the measured string is the
      // rendered string; letter-spacing is passed in for the same reason.
      // At shallow levels each industry IS its own supersector, so the band
      // would just repeat the tile beneath it. Drop it and give the space back.
      const redundant =
        group.rows.length === 1 && group.rows[0].item.n === group.name;
      const showBand = !redundant && cell.h > 52 && cell.w > 70;
      if (showBand) {
        const shown = group.name.toUpperCase();
        const fitted = wrapText(shown, cell.w - 10, 11, 1, 700, 0.04);
        if (fitted) {
          const t = document.createElementNS(SVG_NS, "text");
          t.setAttribute("class", "grouplabel");
          t.setAttribute("x", cell.x + 5);
          t.setAttribute("y", cell.y + 12);
          t.textContent = fitted.truncated ? `${fitted.lines[0]}…` : fitted.lines[0];
          g.appendChild(t);
        }
      }

      const innerY = cell.y + (showBand ? GROUP_LABEL_H : 2);
      const innerH = cell.h - (showBand ? GROUP_LABEL_H : 2) - 2;
      const tiles = group.rows.map((r) => ({
        row: r,
        value: Math.abs(r.value ?? 0) || 1e-9,
      }));
      for (const t of squarify(tiles, cell.x + 2, innerY, cell.w - 4, innerH)) {
        g.appendChild(tileNode(t, maxAbs, pal, q));
      }
      svg.appendChild(g);
    }

    updateChrome(maxAbs);
    postHeight();
  }

  /* Level 1 is four CES aggregates that overlap: Total private already
     contains Goods-producing and Private service-providing, and
     Service-providing contains Private service-providing plus Government.
     Their tiles sum to far more than Total nonfarm, so say so. */
  function updateLevelNote(rows) {
    const note = $("#levelnote");

    if (state.level === 1 && !state.drill) {
      note.hidden = false;
      note.textContent =
        "These four are overlapping CES aggregates, not a partition — Total " +
        "private already includes Goods-producing and Private service-providing. " +
        "Their tiles do not sum to Total nonfarm; level 0 shows that figure.";
      return;
    }

    /* A treemap reads as parts-of-a-whole, but CES only publishes *some*
       children for many parents, so the tiles genuinely do not sum to the
       parent. Nothing here is scaled or padded to make them - so when the
       shortfall is material, say how big it is rather than let the geometry
       imply completeness. */
    if (state.drill) {
      const parent = byCode.get(state.drill);
      const idx = labelToIdx.get(state.base);
      const whole = valueAt(parent, idx);
      let shown = 0;
      let counted = 0;
      for (const row of rows) {
        const v = valueAt(row.item, idx);
        if (v !== null) { shown += v; counted++; }
      }
      if (whole && counted && shown / whole < 0.99) {
        note.hidden = false;
        note.textContent =
          `The ${counted} ${counted === 1 ? "industry" : "industries"} shown ` +
          `cover${counted === 1 ? "s" : ""} ` +
          `${Math.round((shown / whole) * 100)}% of ${parent.n} employment — ` +
          `CES does not publish the rest separately at this level. Tiles are ` +
          `actual reported values and are not scaled to sum to the parent.`;
        return;
      }
    }
    note.hidden = true;
  }

  /* An iframe cannot resize itself. Publish the content height so a host that
     wants an auto-sizing embed can listen; hosts that set a fixed height just
     ignore it, and the embed layout above already fits that case. */
  function postHeight() {
    if (!EMBEDDED) return;
    const height = Math.ceil(
      Math.max(
        document.documentElement.scrollHeight,
        document.body ? document.body.scrollHeight : 0
      )
    );
    if (height === postHeight.last) return;
    postHeight.last = height;
    try {
      parent.postMessage({ type: "nfp-treemap:height", height }, "*");
    } catch { /* cross-origin parents may refuse; nothing to do */ }
  }

  function tileNode(cell, maxAbs, pal, query) {
    const { row } = cell.node;
    const item = row.item;
    const drillable = hasChildren(item.c);

    const g = document.createElementNS(SVG_NS, "g");
    g.setAttribute("class", `tile${drillable ? " drillable" : ""}`);
    g.setAttribute("tabindex", "0");
    g.setAttribute("role", "button");
    g.dataset.code = item.c;
    const changeText = row.value === null
      ? "no data for this period"
      : fmtValue(row.value, state.metric);
    g.setAttribute(
      "aria-label",
      `${item.n}, ${item.ssn}, ${changeText}${drillable ? ", has sub-industries" : ""}`
    );

    if (query) {
      const hit = item.n.toLowerCase().includes(query);
      g.classList.add(hit ? "hit" : "dimmed");
    }

    const rect = document.createElementNS(SVG_NS, "rect");
    rect.setAttribute("x", cell.x); rect.setAttribute("y", cell.y);
    rect.setAttribute("width", Math.max(0, cell.w));
    rect.setAttribute("height", Math.max(0, cell.h));
    rect.setAttribute("fill", colorFor(row.value, maxAbs, pal));
    g.appendChild(rect);

    // Label sizing scales with the tile; anything that cannot fit a whole word
    // gets no label rather than a clipped one.
    if (cell.w >= 46 && cell.h >= 26) {
      // A very large tile (a shallow level, or a dominant industry) looks
      // broken with 13px type marooned in the corner; let type grow with it.
      const maxFont = cell.w > 400 && cell.h > 110 ? 22 : 13;
      const size = Math.max(9, Math.min(maxFont, Math.round(Math.min(cell.w / 9, cell.h / 4))));
      const lineH = size + 2;
      const maxLines = Math.max(1, Math.floor((cell.h - 8) / lineH) - (cell.h > 44 ? 1 : 0));
      const fitted = wrapText(item.n, cell.w - 8, size, maxLines, 600);
      if (fitted) {
        const ink = labelInk(row.value, maxAbs);
        const text = document.createElementNS(SVG_NS, "text");
        text.setAttribute("class", "tilelabel");
        text.setAttribute("x", cell.x + 4);
        text.setAttribute("y", cell.y + size + 3);
        text.setAttribute("fill", ink);
        text.setAttribute("font-size", size);
        for (let i = 0; i < fitted.lines.length; i++) {
          const tspan = document.createElementNS(SVG_NS, "tspan");
          tspan.setAttribute("class", "name");
          tspan.setAttribute("x", cell.x + 4);
          if (i) tspan.setAttribute("dy", lineH);
          tspan.textContent =
            fitted.truncated && i === fitted.lines.length - 1
              ? `${fitted.lines[i]}…`
              : fitted.lines[i];
          text.appendChild(tspan);
        }
        const valueLine = changeText;
        if (
          cell.h > (fitted.lines.length + 1) * lineH + 8 &&
          textWidth(valueLine, size, 400) <= cell.w - 8
        ) {
          const tspan = document.createElementNS(SVG_NS, "tspan");
          tspan.setAttribute("class", "val");
          tspan.setAttribute("x", cell.x + 4);
          tspan.setAttribute("dy", lineH);
          tspan.textContent = valueLine;
          text.appendChild(tspan);
        }
        g.appendChild(text);
      }
    }

    g.addEventListener("pointerenter", (e) => showTip(e, item, row.value));
    g.addEventListener("pointermove", moveTip);
    g.addEventListener("pointerleave", hideTip);
    g.addEventListener("focus", (e) => showTip(e, item, row.value, true));
    g.addEventListener("blur", hideTip);
    g.addEventListener("click", () => { if (drillable) drillTo(item.c); });
    g.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); if (drillable) drillTo(item.c); }
      if (e.key === "Escape") { e.preventDefault(); drillUp(); }
    });
    return g;
  }

  // Dark tile fills need light ink; the pale inner steps need dark ink.
  function labelInk(value, maxAbs) {
    if (value === null || maxAbs <= 0) return cssVar("--text-primary");
    const t = Math.min(1, Math.abs(value) / maxAbs);
    const dark = document.documentElement.dataset.theme === "dark" ||
      (!document.documentElement.dataset.theme &&
        matchMedia("(prefers-color-scheme: dark)").matches);
    if (state.palette === "classic") return t > 0.62 ? "#ffffff" : "#0b0b0b";
    if (dark) return t > 0.55 ? "#0b0b0b" : "#ffffff";
    return t > 0.5 ? "#ffffff" : "#0b0b0b";
  }

  // ---------------------------------------------------------------- tooltip
  const tip = $("#tip");

  function showTip(evt, item, value, pinned = false) {
    const idx = labelToIdx.get(state.base);
    const h = HORIZONS[state.horizon];
    const stat = anomaly(item, idx, h, state.metric);
    const level = valueAt(item, idx);

    const parts = [];
    parts.push(`<div class="ss">${esc(item.ssn)}</div>`);
    parts.push(`<div class="nm">${esc(item.n)}</div>`);

    if (item.naics) {
      const codes = item.naics.codes
        .filter((c) => c.title)
        .map((c) => {
          const rolled = c.match === "rolled_up"
            ? ` <span class="flag">(nearest published: ${esc(c.resolved_code)})</span>`
            : "";
          return `<span class="code">${esc(c.code)}</span> — ${esc(c.title)}${rolled}`;
        });
      if (codes.length) {
        const partial = item.naics.partial
          ? `<div class="flag">CES sub-part of NAICS ${esc(item.naics.codes[0].code)}</div>`
          : "";
        const desc = item.naics.description
          ? `<span class="desc">${esc(trim(item.naics.description, 320))}</span>`
          : "";
        parts.push(`<div class="naics">${codes.join("<br>")}${partial}${desc}</div>`);
      }
    }

    parts.push(
      `<div class="chg">All employees: <b>${fmtLevel(level)}</b>` +
      `<br>${state.horizon} change: <b>${fmtValue(value, state.metric)}</b>` +
      (state.metric === "abs"
        ? ` <span class="note">(${fmtPct(change(item, idx, h, "pct"))})</span>`
        : ` <span class="note">(${fmtAbs(change(item, idx, h, "abs"))})</span>`) +
      `</div>`
    );

    if (stat && stat.spansDisruption) {
      parts.push(
        `<div class="anom"><span class="note">This ${state.horizon} window spans the ` +
        `2020–22 pandemic disruption, so it is not comparable with the rest of this ` +
        `industry's history. No score shown.</span></div>`
      );
    } else if (stat && !stat.insufficient) {
      /* Rank direction is not the sign of the change: a +2.81M gain can still
         sit below almost every comparable window. Saying "larger drop than
         100%" of a gain was flatly wrong, so the sentence states the value and
         where it ranks, and never calls a gain a drop. */
      const above = stat.z >= 0;
      const share = Math.round(above ? stat.pct : 100 - stat.pct);
      parts.push(
        `<div class="anom"><span class="badge">${above ? "▲" : "▼"} ${stat.label}</span> — ` +
        `robust z = ${stat.z.toFixed(2)}, ${ordinal(Math.round(stat.pct))} percentile<br>` +
        `<span class="note">${fmtValue(stat.current, state.metric)} is ` +
        `${above ? "higher" : "lower"} than ${share}% of ${state.horizon} changes over ` +
        `the last ${Math.round(stat.spanMonths / 12)} years ` +
        `(n=${stat.n}, pandemic windows excluded)</span></div>`
      );
    } else if (stat) {
      parts.push(
        `<div class="anom"><span class="note">Not enough comparable history to score a ` +
        `${state.horizon} change — ${Math.floor(stat.independent || 0)} independent ` +
        `windows, need ${ANOM.minIndependent}.</span></div>`
      );
    }

    parts.push(sparkline(item, idx));
    parts.push(
      `<div class="sparkcap">All employees, thousands, ` +
      `${LABELS[item.s - PERIOD_START]} – ${LABELS[item.s + item.vals.length - 1 - PERIOD_START]}` +
      ` · shaded = NBER recessions</div>`
    );

    tip.innerHTML = parts.join("");
    tip.classList.add("on");
    if (pinned) {
      const box = evt.target.getBoundingClientRect();
      placeTip(box.left + box.width / 2, box.top + box.height / 2);
    } else {
      moveTip(evt);
    }
  }

  function sparkline(item, markIdx) {
    const W = 336, H = 74, PAD = 2;
    const vals = item.vals;
    let lo = Infinity, hi = -Infinity;
    for (const v of vals) { if (v < lo) lo = v; if (v > hi) hi = v; }
    if (!(hi > lo)) { hi = lo + 1; }
    const x = (i) => PAD + (i / Math.max(1, vals.length - 1)) * (W - 2 * PAD);
    const y = (v) => PAD + (1 - (v - lo) / (hi - lo)) * (H - 2 * PAD);

    let bands = "";
    for (const [from, to] of RECESSIONS) {
      const a = labelToIdx.get(from), b = labelToIdx.get(to);
      if (a === undefined || b === undefined) continue;
      const i0 = a - item.s, i1 = b - item.s;
      if (i1 < 0 || i0 > vals.length - 1) continue;
      const xa = x(Math.max(0, i0)), xb = x(Math.min(vals.length - 1, i1));
      bands += `<rect x="${xa.toFixed(1)}" y="0" width="${Math.max(0.8, xb - xa).toFixed(1)}" height="${H}" fill="var(--gridline)"/>`;
    }

    let d = "";
    for (let i = 0; i < vals.length; i++) {
      d += `${i ? "L" : "M"}${x(i).toFixed(1)},${y(vals[i]).toFixed(1)}`;
    }

    const mi = markIdx - item.s;
    let marker = "";
    if (mi >= 0 && mi < vals.length) {
      marker =
        `<line x1="${x(mi).toFixed(1)}" y1="0" x2="${x(mi).toFixed(1)}" y2="${H}" stroke="var(--muted)" stroke-width="1" stroke-dasharray="2 2"/>` +
        `<circle cx="${x(mi).toFixed(1)}" cy="${y(vals[mi]).toFixed(1)}" r="3" fill="var(--text-primary)" stroke="var(--surface-1)" stroke-width="1.5"/>`;
    }
    // width:100% + viewBox so the sparkline shrinks with a clamped tooltip on
    // a phone instead of forcing it wider than the screen.
    return `<svg class="spark" width="100%" height="${H}" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">${bands}` +
      `<path d="${d}" fill="none" stroke="var(--focus)" stroke-width="2" stroke-linejoin="round"/>${marker}</svg>`;
  }

  function placeTip(cx, cy) {
    const r = tip.getBoundingClientRect();
    let left = cx + 16;
    let top = cy + 16;
    if (left + r.width > innerWidth - 8) left = cx - r.width - 16;
    if (left < 8) left = 8;
    if (top + r.height > innerHeight - 8) top = Math.max(8, cy - r.height - 16);
    tip.style.left = `${left}px`;
    tip.style.top = `${top}px`;
  }
  const moveTip = (e) => placeTip(e.clientX, e.clientY);
  const hideTip = () => tip.classList.remove("on");

  // ---------------------------------------------------------------- chrome
  function updateChrome(maxAbs) {
    const pal = ramp();
    const stops = [...[...pal.loss].reverse(), pal.mid, ...pal.gain];
    $("#legendbar").style.background = `linear-gradient(90deg, ${stops.join(",")})`;
    $("#legendlo").textContent = fmtValue(-maxAbs, state.metric);
    $("#legendhi").textContent = fmtValue(maxAbs, state.metric);
    $("#legendcap").textContent =
      state.metric === "pct"
        ? "Percent change in employees (colour); tile area = absolute change"
        : "Change in employees, thousands (colour and tile area)";

    const scope = state.drill ? byCode.get(state.drill).n : "all industries";
    $("#charttitle").textContent =
      `Change in Employees by Industry — ${prettyMonth(state.base)} versus ${state.horizon} prior` +
      ` · level ${state.level} · ${scope}`;
    renderCrumbs();
  }

  /* Missing tiles have two completely different causes, and blaming the wrong
     one is worse than saying nothing. At the newest month the detail simply is
     not published yet. At an early base period the series did not exist: most
     CES industry detail begins in 1990, so February 1939 is missing 238 of 240
     level-5 industries because they had not been broken out, not because BLS
     is running late. Classify, then say which. */
  function updateLagNote(rows) {
    const note = $("#lagnote");
    const idx = labelToIdx.get(state.base);
    const h = HORIZONS[state.horizon];

    let notYet = 0;      // series ends before this month: awaiting publication
    let notBorn = 0;     // series starts after this month (or after base - h)
    let earliestFull = null;   // newest start among the industries shown
    let latestFull = null;     // oldest end among the industries shown

    for (const row of rows) {
      const start = row.item.s;
      const end = row.item.s + row.item.vals.length - 1;
      earliestFull = earliestFull === null ? start : Math.max(earliestFull, start);
      latestFull = latestFull === null ? end : Math.min(latestFull, end);
      if (row.value !== null) continue;
      if (idx - h < start) notBorn++;
      else if (idx > end) notYet++;
      else notBorn++;  // an interior gap; treat as not covered by the series
    }

    const missing = notYet + notBorn;
    if (!missing) { note.hidden = true; return; }
    note.hidden = false;

    const parts = [
      `${missing} of ${rows.length} industries have no value for ` +
      `${prettyMonth(state.base)}${h > 1 ? " or its comparison month" : ""}.`,
    ];

    if (notBorn) {
      const from = earliestFull !== null && earliestFull - PERIOD_START >= 0
        ? prettyMonth(LABELS[earliestFull - PERIOD_START]) : null;
      parts.push(
        `CES had not broken them out this far back: most industry detail ` +
        `begins in 1990 and only the broad aggregates reach 1939.` +
        (from ? ` Every industry at this level has data from ${from} onward.` : "")
      );
    }
    if (notYet) {
      const to = latestFull !== null && latestFull - PERIOD_START >= 0
        ? prettyMonth(LABELS[latestFull - PERIOD_START]) : null;
      parts.push(
        `BLS publishes detailed industries about a month behind the headline ` +
        `aggregates.` +
        (to && to !== state.base
          ? ` The newest month covering all of them is ${to}.` : "")
      );
    }

    note.textContent = parts.join(" ");
  }

  function renderCrumbs() {
    const box = $("#crumbs");
    box.textContent = "";
    const chain = state.drill ? byCode.get(state.drill).chain : [];
    const nodes = [{ code: null, name: "All industries" }].concat(
      chain.map((c) => ({ code: c, name: byCode.get(c).n }))
    );
    nodes.forEach((n, i) => {
      if (i) {
        const sep = document.createElement("span");
        sep.className = "sep";
        sep.textContent = "›";
        box.appendChild(sep);
      }
      const b = document.createElement("button");
      b.className = "crumb";
      b.textContent = n.name;
      if (i === nodes.length - 1) b.setAttribute("aria-current", "page");
      else b.addEventListener("click", () => drillTo(n.code));
      box.appendChild(b);
    });
  }

  function drillTo(code) {
    state.drill = code;
    if (code) {
      const node = byCode.get(code);
      const deeper = LEVELS.filter((l) => l > node.l);
      if (!deeper.length) return;
      if (state.level <= node.l) state.level = deeper[0];
    }
    hideTip();
    render();
  }

  function drillUp() {
    if (!state.drill) return;
    const node = byCode.get(state.drill);
    drillTo(node.p || null);
  }

  // ---------------------------------------------------------------- controls
  function syncControls() {
    $("#base").value = state.base;
    $("#horizon").value = state.horizon;
    $("#palette").value = state.palette;
    $("#q").value = state.highlight;

    // Level 0 is Total nonfarm on its own - the headline payroll number, with
    // the same anomaly score and full history as any other tile.
    if (state.drill && !byCode.has(state.drill)) state.drill = null;
    const min = state.drill ? byCode.get(state.drill).l + 1 : 0;
    const sel = $("#level");
    const want = String(state.level);
    sel.textContent = "";
    for (const l of LEVELS.filter((l) => l >= min)) {
      const o = document.createElement("option");
      o.value = String(l);
      o.textContent = l === 0 ? "Level 0 — Total nonfarm" : `Level ${l}`;
      sel.appendChild(o);
    }
    if (![...sel.options].some((o) => o.value === want)) {
      state.level = Number(sel.options[0]?.value ?? state.level);
    }
    sel.value = String(state.level);

    for (const b of document.querySelectorAll("#metric button")) {
      b.setAttribute("aria-pressed", String(b.dataset.metric === state.metric));
    }
  }

  function initControls() {
    const base = $("#base");
    for (let i = LABELS.length - 1; i >= 0; i--) {
      const o = document.createElement("option");
      o.value = LABELS[i];
      o.textContent = prettyMonth(LABELS[i]);
      base.appendChild(o);
    }
    const horizon = $("#horizon");
    for (const key of Object.keys(HORIZONS)) {
      const o = document.createElement("option");
      o.value = key;
      o.textContent = `vs ${key} prior`;
      horizon.appendChild(o);
    }

    base.addEventListener("change", () => { state.base = base.value; render(); });
    horizon.addEventListener("change", () => { state.horizon = horizon.value; render(); });
    $("#level").addEventListener("change", (e) => { state.level = +e.target.value; render(); });
    $("#palette").addEventListener("change", (e) => { state.palette = e.target.value; render(); });

    let timer;
    $("#q").addEventListener("input", (e) => {
      clearTimeout(timer);
      timer = setTimeout(() => { state.highlight = e.target.value; render(); }, 140);
    });

    for (const b of document.querySelectorAll("#metric button")) {
      b.addEventListener("click", () => { state.metric = b.dataset.metric; render(); });
    }
    $("#up").addEventListener("click", drillUp);
    $("#csv").addEventListener("click", exportCsv);
    $("#png").addEventListener("click", exportPng);
    $("#link").addEventListener("click", copyLink);

    addEventListener("keydown", (e) => {
      if (e.key === "Escape" && state.drill && e.target === document.body) drillUp();
    });
    // A window resize event does not fire when only the embedding container
    // changes size, so observe the element as well.
    let raf;
    const reflow = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(render); };
    addEventListener("resize", reflow);
    if (window.ResizeObserver) {
      let lastWidth = containerWidth();
      new ResizeObserver(() => {
        const width = containerWidth();
        if (width !== lastWidth) { lastWidth = width; reflow(); }
      }).observe(document.querySelector(".wrap"));
    }
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
  }

  // ---------------------------------------------------------------- export
  /* Two hosts, two mechanisms. Opened as a local file, an anchor with
     [download] works. Published as an Artifact, the viewer sandbox blocks
     page-initiated downloads outright and the file must be handed over through
     window.claude.downloads.save(), which asks the viewer to confirm. */
  async function download(blob, filename, button) {
    const saver = window.claude && window.claude.downloads;
    if (saver) {
      try {
        await saver.save({ filename, data: blob });
        flash(button, "Saved");
      } catch (err) {
        // .csv sits in the extended allowlist and may be off for this view;
        // the bytes are still valid CSV under a .txt name.
        if (err && err.code === "extension_not_enabled" && filename.endsWith(".csv")) {
          try {
            await saver.save({ filename: filename.replace(/\.csv$/, ".txt"), data: blob });
            flash(button, "Saved as .txt");
            return;
          } catch (retryErr) {
            flashSaveError(button, retryErr);
            return;
          }
        }
        flashSaveError(button, err);
      }
      return;
    }

    try {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 4000);
      flash(button, "Saved");
    } catch (err) {
      flash(button, "Download blocked here");
    }
  }

  function flashSaveError(button, err) {
    const code = (err && err.code) || "unavailable";
    flash(button, {
      declined: "Cancelled",            // viewer said no; never auto-retry
      rate_limited: "Try again shortly",
      too_large: "Too large to save",
      bad_request: "Export failed",
      transform_error: "Export failed",
    }[code] || "Saving unavailable");
  }

  function flash(button, message) {
    const original = button.textContent;
    button.textContent = message;
    setTimeout(() => { button.textContent = original; }, 2200);
  }

  function buildCsv() {
    const idx = labelToIdx.get(state.base);
    const h = HORIZONS[state.horizon];
    const head = [
      "industry_code", "industry_name", "supersector", "display_level", "naics_codes",
      "employees_thousands", `abs_change_${state.horizon}`, `pct_change_${state.horizon}`,
      "z_score", "percentile", "anomaly_label",
    ];
    const lines = [head.join(",")];
    for (const { item } of currentRows()) {
      const stat = anomaly(item, idx, h, state.metric);
      const naics = item.naics ? item.naics.codes.map((c) => c.code).join(" ") : "";
      lines.push([
        item.c, item.n, item.ssn, item.l, naics,
        fmtNum(valueAt(item, idx)),
        fmtNum(change(item, idx, h, "abs")),
        fmtNum(change(item, idx, h, "pct")),
        scored(stat) ? stat.z.toFixed(3) : "",
        scored(stat) ? stat.pct.toFixed(1) : "",
        scored(stat) ? stat.label
          : stat && stat.spansDisruption ? "spans 2020-22 disruption"
          : "insufficient history",
      ].map(csvCell).join(","));
    }
    return lines.join("\n");
  }

  function exportCsv() {
    download(
      new Blob([buildCsv()], { type: "text/csv;charset=utf-8" }),
      `ces-treemap-${state.base}-${state.horizon}-level${state.level}.csv`,
      $("#csv")
    );
  }

  function exportPng() {
    const button = $("#png");
    const clone = svg.cloneNode(true);
    const vb = svg.getAttribute("viewBox").split(" ").map(Number);
    const scale = 2;
    clone.setAttribute("width", vb[2]);
    clone.setAttribute("height", vb[3]);
    // Inline the computed values of the CSS variables the SVG references.
    const style = document.createElementNS(SVG_NS, "style");
    style.textContent = `
      text { font-family: ${FONT_STACK}; }
      .grouplabel { font-size: 11px; font-weight: 700; letter-spacing: .04em;
        fill: ${cssVar("--text-secondary")}; text-transform: uppercase; }
      .groupframe { fill: none; stroke: ${cssVar("--border")}; }
      .tile rect { stroke: ${cssVar("--surface-1")}; stroke-width: 2; }
      .tilelabel tspan.name { font-weight: 600; }`;
    clone.insertBefore(style, clone.firstChild);

    const blob = new Blob(
      [`<svg xmlns="${SVG_NS}" ${[...clone.attributes].map((a) => `${a.name}="${a.value}"`).join(" ")}>${clone.innerHTML}</svg>`],
      { type: "image/svg+xml;charset=utf-8" }
    );
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = vb[2] * scale;
      canvas.height = vb[3] * scale;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = cssVar("--surface-1");
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.scale(scale, scale);
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);
      canvas.toBlob((b) =>
        download(b, `ces-treemap-${state.base}-${state.horizon}-level${state.level}.png`, button)
      );
    };
    img.onerror = () => { URL.revokeObjectURL(url); flash(button, "PNG failed"); };
    img.src = url;
  }

  async function copyLink() {
    writeHash();
    try {
      await navigator.clipboard.writeText(location.href);
      flash($("#link"), "Link copied");
    } catch {
      flash($("#link"), "Copy from the address bar");
    }
  }

  // ---------------------------------------------------------------- helpers
  const esc = (s) =>
    String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const trim = (s, n) => (s.length <= n ? s : `${s.slice(0, n).replace(/\s+\S*$/, "")}…`);
  const fmtNum = (v) => (v === null || v === undefined ? "" : v.toFixed(3));
  const csvCell = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
  const ordinal = (n) => {
    const s = ["th", "st", "nd", "rd"];
    const v = n % 100;
    return n + (s[(v - 20) % 10] || s[v] || s[0]);
  };

  // Test seam: lets tests/test_frontend.py exercise the real shipped
  // implementations rather than a reimplementation of them.
  window.__treemap = {
    anomaly, change, squarify, wrapText, colorFor, buildCsv,
    byCode, valueAt, labelToIdx, state, render,
  };

  // ---------------------------------------------------------------- boot
  readHash();
  initControls();
  const m = PAYLOAD.meta;
  $("#stamp").textContent =
    `${m.series} seasonally adjusted CES series · ${Number(m.observations).toLocaleString()} observations · ` +
    `latest published ${prettyMonth(m.latest_period)} · fetched ${m.last_fetch?.slice(0, 10)} · ` +
    `source: BLS API v2 + Census 2022 NAICS`;
  render();
  // The first pass sizes the chart against estimated chrome heights. Re-run
  // once after layout settles so the embedded fit uses measured values.
  if (EMBEDDED) requestAnimationFrame(() => requestAnimationFrame(render));
})();
