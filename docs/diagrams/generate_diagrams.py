"""Generate the four hand-authored diagrams for docs/ecb-mode-unsafe.md.

The SVGs are theme-aware: theme-dependent colors (card/panel backgrounds, ink and
muted text, neutral fills, arrows) are CSS variables with a `prefers-color-scheme:
dark` override, so a single committed SVG renders correctly in both GitHub themes
when embedded as an image. Semantic colors (navy, red=leak/danger, green=safe,
purple, amber) stay fixed — they read on either background.

Run: `python3 docs/diagrams/generate_diagrams.py` (writes the .svg files beside it).
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

SANS = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
# sentinels routed to CSS classes (theme-aware); real values live in --vars below
INK, MUTED, NEU_F, NEU_S = "@ink", "@muted", "@neuf", "@neus"
ARROW = "@arw"
# fixed semantic colors (read on both themes)
NAVY = "#1f3a5f"
RED, GREEN, PURPLE, AMBER, GRAY, BLUE = "#dc2626", "#16a34a", "#6d28d9", "#b45309", "#64748b", "#2563eb"

STYLE = (
 '<style>'
 ':root{--card:#ffffff;--panel:#f8fafc;--border:#e2e8f0;--ink:#0f172a;--muted:#475569;'
 '--neuf:#f1f5f9;--neus:#cbd5e1;--arw:#94a3b8}'
 '@media (prefers-color-scheme:dark){:root{--card:#0d1117;--panel:#161b22;--border:#30363d;'
 '--ink:#e6edf3;--muted:#9aa4b2;--neuf:#1c2330;--neus:#3d444d;--arw:#6e7681}}'
 '.cardb{fill:var(--card);stroke:var(--border)}.card{fill:var(--card)}'
 '.panel{fill:var(--panel);stroke:var(--border)}'
 '.neu{fill:var(--neuf);stroke:var(--neus)}.cellA{fill:var(--neuf);stroke:var(--neus)}'
 '.xor{fill:var(--card);stroke:var(--muted)}'
 '.ink{fill:var(--ink)}.muted{fill:var(--muted)}'
 '.arw{stroke:var(--arw)}.arwhead{fill:var(--arw)}'
 '</style>')

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _fillattr(color):
    return {INK: 'class="ink"', MUTED: 'class="muted"'}.get(color, f'fill="{color}"')

def text(x, y, s, size=13, fill=INK, anchor="middle", weight="400", mono=False, lh=15):
    font = MONO if mono else SANS
    lines = s.split("\n")
    parts = [f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" {_fillattr(fill)} '
             f'text-anchor="{anchor}" font-weight="{weight}">']
    for i, ln in enumerate(lines):
        parts.append(f'<tspan x="{x}" dy="{0 if i == 0 else lh}">{esc(ln)}</tspan>')
    parts.append('</text>')
    return "".join(parts)

def box(x, y, w, h, label, fill=NEU_F, stroke=NEU_S, tc=INK, mono=False, rx=9, size=13, weight="600", lh=15, sw=1.5):
    n = len(label.split("\n"))
    cx, cy = x + w / 2, y + h / 2
    first = cy - (n - 1) * lh / 2 + size / 3
    if fill == NEU_F and stroke == NEU_S:
        rect = f'<rect class="neu" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" stroke-width="{sw}"/>'
    else:
        rect = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    return rect + text(cx, first, label, size=size, fill=tc, mono=mono, weight=weight, lh=lh)

def arrow(x1, y1, x2, y2, dashed=False, color=ARROW, sw=2):
    da = ' stroke-dasharray="6 5"' if dashed else ''
    st = 'class="arw"' if color == ARROW else f'stroke="{color}"'
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {st} stroke-width="{sw}"{da} marker-end="url(#arw)"/>'

def path(d, dashed=False, color=ARROW, sw=2):
    da = ' stroke-dasharray="6 5"' if dashed else ''
    st = 'class="arw"' if color == ARROW else f'stroke="{color}"'
    return f'<path d="{d}" fill="none" {st} stroke-width="{sw}"{da} marker-end="url(#arw)"/>'

def alabel(x, y, s, size=11, fill=MUTED):
    w = len(s) * size * 0.56 + 10
    return (f'<rect class="card" x="{x - w / 2}" y="{y - size + 2}" width="{w}" height="{size + 6}" rx="4" opacity="0.95"/>'
            + text(x, y + 3, s, size=size, fill=fill, weight="500"))

def svg(w, h, title, body, subtitle=None):
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{SANS}">'
            + STYLE
            + '<defs><marker id="arw" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">'
            + '<path d="M0,0 L8,3 L0,6 z" class="arwhead"/></marker></defs>'
            + f'<rect class="cardb" x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" stroke-width="2"/>'
            + text(w / 2, 32, title, size=17, fill=INK, weight="700"))
    if subtitle:
        head += text(w / 2, 52, subtitle, size=12, fill=MUTED)
    return head + body + '</svg>'

W = 900

def panel(x, y, w, h):
    return f'<rect class="panel" x="{x}" y="{y}" width="{w}" height="{h}" rx="10" stroke-width="1.5"/>'

# ---------------- Diagram 2: taxonomy ----------------
def d2():
    b = [box(W / 2 - 80, 62, 160, 44, "AES-ECB", fill=NAVY, stroke="#0d1b2a", tc="#fff", size=15, weight="700")]
    r1 = (90, 150, 320, 58)
    r2 = (490, 150, 320, 58)
    b.append(box(*r1, "Root cause 1 — Determinism\nequal plaintext block → equal ciphertext block", fill=NAVY, stroke="#0d1b2a", tc="#fff", size=12.5))
    b.append(box(*r2, "Root cause 2 — No integrity / no chaining\nblocks independent and unauthenticated", fill=NAVY, stroke="#0d1b2a", tc="#fff", size=12.5))
    b.append(arrow(W / 2, 106, r1[0] + r1[2] / 2, r1[1] - 2))
    b.append(arrow(W / 2, 106, r2[0] + r2[2] / 2, r2[1] - 2))
    vy, vh = 258, 66
    vs = [
        (30, 190, "Vector 1", "Pattern & structure leakage", "passive", BLUE),
        (232, 190, "Vector 2", "Equality & frequency inference", "passive / statistical", BLUE),
        (434, 180, "Vector 3", "Byte-at-a-time recovery", "active oracle", BLUE),
        (640, 230, "Vector 4", "Block malleability / cut-and-paste", "active splice", AMBER),
    ]
    for x, w, vt, desc, mode, ac in vs:
        b.append(f'<rect class="neu" x="{x}" y="{vy}" width="{w}" height="{vh}" rx="9" stroke-width="1.5"/>')
        b.append(f'<rect x="{x}" y="{vy}" width="6" height="{vh}" rx="3" fill="{ac}"/>')
        cx = x + w / 2
        b.append(text(cx, vy + 22, vt, size=13, fill=INK, weight="700"))
        b.append(text(cx, vy + 40, desc, size=11.5, fill=INK))
        b.append(text(cx, vy + 56, mode, size=11, fill=MUTED, weight="500"))
    r1c = r1[0] + r1[2] / 2
    for x, w, *_ in vs[:3]:
        b.append(arrow(r1c, r1[1] + r1[3], x + w / 2, vy - 2))
    b.append(arrow(r2[0] + r2[2] / 2, r2[1] + r2[3], vs[3][0] + vs[3][1] / 2, vy - 2))
    return svg(W, 348, "ECB's two root causes and four attack vectors", "".join(b),
               subtitle="every vector follows from one or both root causes — there is no third")

# ---------------- byte-cell block ----------------
def block_cells(x, y, cells, cw=34, ch=30):
    out = []
    for i, (lbl, kind) in enumerate(cells):
        cx = x + i * cw
        if kind == "known":
            out.append(f'<rect x="{cx}" y="{y}" width="{cw}" height="{ch}" fill="#fef3c7" stroke="{AMBER}" stroke-width="1.2"/>')
            out.append(text(cx + cw / 2, y + ch / 2 + 4.5, lbl, size=12, fill="#92400e", mono=True, weight="700"))
        elif kind == "unknown":
            out.append(f'<rect x="{cx}" y="{y}" width="{cw}" height="{ch}" fill="#ede9fe" stroke="{PURPLE}" stroke-width="1.2"/>')
            out.append(text(cx + cw / 2, y + ch / 2 + 4.5, lbl, size=12, fill="#5b21b6", mono=True, weight="700"))
        else:
            out.append(f'<rect class="cellA" x="{cx}" y="{y}" width="{cw}" height="{ch}" stroke-width="1.2"/>')
            out.append(text(cx + cw / 2, y + ch / 2 + 4.5, lbl, size=12, fill=MUTED, mono=True, weight="700"))
    return "".join(out)

# ---------------- Diagram 3: byte-at-a-time ----------------
def d3():
    b = [box(40, 62, W - 80, 40, "Oracle:   C = AES-ECB( attacker_input ‖ secret ),   fixed key — never revealed",
             fill=NAVY, stroke="#0d1b2a", tc="#fff", size=13)]
    bx = (W - 16 * 34) / 2

    def step(y0, title, cap1, tcells, cap2, pcells):
        o = [panel(30, y0, W - 60, 168),
             text(48, y0 + 24, title, size=13, fill=INK, weight="700", anchor="start"),
             text(bx, y0 + 46, cap1, size=11.5, fill=MUTED, anchor="start"),
             block_cells(bx, y0 + 54, tcells),
             text(bx, y0 + 110, cap2, size=11.5, fill=MUTED, anchor="start"),
             block_cells(bx, y0 + 118, pcells)]
        return "".join(o)
    A = ("A", "A")
    b.append(step(118, "Step 1 · recover secret byte 0  —  send 15 filler bytes",
                  "TARGET  ·  encrypt these 16 bytes, keep ciphertext block 0", [A] * 15 + [("S0", "known")],
                  "PROBE  ·  try candidate = 0..255 in the last slot — block matches when ? = S0", [A] * 15 + [("?", "unknown")]))
    b.append(text(W / 2, 306, "▼   shift the filler down by one byte", size=12, fill=MUTED, weight="600"))
    b.append(step(320, "Step 2 · recover secret byte 1  —  send 14 filler bytes",
                  "TARGET  ·  S0 is already known from step 1", [A] * 14 + [("S0", "known"), ("S1", "known")],
                  "PROBE  ·  match now reveals S1 — then shift and repeat for every byte", [A] * 14 + [("S0", "known"), ("?", "unknown")]))
    b.append(text(W / 2, 508, "▼   repeat for each byte", size=12, fill=MUTED, weight="600"))
    b.append(box(W / 2 - 240, 522, 480, 42, "Full secret recovered in ≈ 256 × L queries — the key is never needed",
                 fill=GREEN, stroke="#15803d", tc="#fff", size=13))
    b.append(text(W / 2, 584, "Scope: run only against a local demonstration oracle (ecb_lab.oracle_attack.make_suffix_oracle), never a third-party service.",
                  size=10.5, fill=MUTED))
    return svg(W, 600, "Vector 3 — chosen-plaintext byte-at-a-time recovery", "".join(b))

# ---------------- Diagram 4: cut-and-paste ----------------
def d4():
    b = []
    bw, bh = 254, 46
    x0 = (W - 3 * bw) / 2

    def tokrow(y, label, blocks):
        o = [text(x0, y - 10, label, size=12.5, fill=INK, weight="700", anchor="start")]
        for i, (txt, kind) in enumerate(blocks):
            x = x0 + i * bw
            if kind == "admin":
                o.append(f'<rect x="{x}" y="{y}" width="{bw - 6}" height="{bh}" rx="8" fill="#fee2e2" stroke="{RED}" stroke-width="1.6"/>')
                tc = "#991b1b"
            elif kind == "drop":
                o.append(f'<rect class="neu" x="{x}" y="{y}" width="{bw - 6}" height="{bh}" rx="8" stroke="{GRAY}" stroke-width="1.6"/>')
                tc = MUTED
                o.append(f'<line x1="{x + 8}" y1="{y + bh - 6}" x2="{x + bw - 14}" y2="{y + 6}" stroke="{GRAY}" stroke-width="1.5" stroke-dasharray="4 3"/>')
            else:
                o.append(f'<rect class="neu" x="{x}" y="{y}" width="{bw - 6}" height="{bh}" rx="8" stroke-width="1.6"/>')
                tc = INK
            o.append(text(x + (bw - 6) / 2, y + 18, f"block {i}", size=10, fill=MUTED, weight="600"))
            o.append(text(x + (bw - 6) / 2, y + 35, txt, size=12, fill=tc, mono=True, weight="600"))
        return "".join(o), [x0 + i * bw + (bw - 6) / 2 for i in range(len(blocks))]
    yD, yB, yF = 88, 196, 322
    d, _ = tokrow(yD, "Donor token  —  attacker email = ‘xxxxxxxxxx’ + admin-padding",
                  [("email=xxxxxxxxxx", "n"), ("admin + padding", "admin"), ("&uid=1000&role=user …", "n")])
    bb, _ = tokrow(yB, "Base token  —  attacker email = ‘aaaaaaaaaaa’ (aligns role= to a block boundary)",
                   [("email=aaaaaaaaaa", "n"), ("a&uid=1000&role=", "n"), ("user + padding", "drop")])
    ff, fxc = tokrow(yF, "Forged token  —  Base blocks 0–1 + Donor’s admin block",
                     [("email=aaaaaaaaaa", "n"), ("a&uid=1000&role=", "n"), ("admin + padding", "admin")])
    b += [d, bb, ff]
    donor_admin_cx = x0 + 1 * bw + (bw - 6) / 2
    forged_admin_cx = fxc[2]
    b.append(path(f"M {donor_admin_cx} {yD + bh} C {donor_admin_cx} {yD + bh + 70}, {forged_admin_cx} {yF - 70}, {forged_admin_cx} {yF - 2}", dashed=True, color=RED))
    b.append(alabel((donor_admin_cx + forged_admin_cx) / 2, yD + bh + 22, "copy this ciphertext block", fill=RED))
    b.append(alabel(x0 + 2 * bw + (bw - 6) / 2, yB + bh + 16, "dropped before splicing", fill=GRAY))
    b.append(box(W / 2 - 250, 392, 500, 42, "Decrypts to role=admin  —  server accepts it; no integrity check to fail",
                 fill=GREEN, stroke="#15803d", tc="#fff", size=13))
    b.append(text(W / 2, 456, "Scope: ProfileService is a self-contained local stand-in; the target key stays in-process, no external system involved.",
                  size=10.5, fill=MUTED))
    return svg(W, 472, "Vector 4 — block cut-and-paste privilege escalation", "".join(b))

# ---------------- Diagram 1: three modes ----------------
def d1():
    b = []

    def lane(y0, title, draw):
        return "".join([panel(24, y0, W - 48, 150),
                        text(40, y0 + 24, title, size=13, fill=INK, weight="700", anchor="start"),
                        draw(y0)])

    def EK(x, y, w=58, h=32):
        return box(x, y, w, h, "Eₖ", fill="#e0e7ff", stroke="#6366f1", tc="#3730a3", size=14, weight="700", rx=7)

    def xor(cx, cy, r=15):
        return (f'<circle class="xor" cx="{cx}" cy="{cy}" r="{r}" stroke-width="1.8"/>'
                + text(cx, cy + 5, "⊕", size=16, fill=MUTED, weight="700"))

    def ecb(y0):
        o = []
        ry1, ry2, h = y0 + 58, y0 + 106, 32
        o.append(box(48, ry1 - 16, 74, h, "P1")); o.append(arrow(122, ry1, 168, ry1))
        o.append(EK(168, ry1 - 16)); o.append(arrow(226, ry1, 272, ry1))
        o.append(box(272, ry1 - 16, 74, h, "C1"))
        o.append(box(48, ry2 - 16, 74, h, "P2 = P1", size=11)); o.append(arrow(122, ry2, 168, ry2))
        o.append(EK(168, ry2 - 16)); o.append(arrow(226, ry2, 272, ry2))
        o.append(box(272, ry2 - 16, 210, h, "C2 = C1  — structure leaks", fill=RED, stroke="#991b1b", tc="#fff", size=12))
        o.append(f'<path d="M 500 {ry1} C 528 {ry1}, 528 {ry2}, 500 {ry2}" fill="none" stroke="{RED}" stroke-width="1.6"/>')
        o.append(text(548, (ry1 + ry2) / 2 + 4, "identical", size=11, fill=RED, weight="700"))
        o.append(text(548, (ry1 + ry2) / 2 + 20, "in → identical out", size=10.5, fill=MUTED))
        return "".join(o)

    def cbc(y0):
        o = []; cy = y0 + 92
        o.append(box(44, cy - 52, 84, 26, "random IV", size=10.5))
        o.append(box(44, cy - 10, 74, 26, "P1", size=11))
        o.append(arrow(128, cy - 39, 169, cy - 10)); o.append(arrow(118, cy + 3, 169, cy - 4))
        o.append(xor(184, cy - 4)); o.append(arrow(199, cy - 4, 236, cy - 4))
        o.append(EK(236, cy - 20)); o.append(arrow(294, cy - 4, 330, cy - 4))
        o.append(box(330, cy - 20, 74, 32, "C1"))
        o.append(box(470, cy - 52, 84, 26, "P2 = P1", size=10.5))
        o.append(xor(560, cy - 4)); o.append(arrow(544, cy - 39, 560, cy - 19))
        o.append(path(f"M 404 {cy - 4} C 430 {cy - 4}, 430 {cy + 34}, 545 {cy + 34} L 545 {cy + 8} L 552 {cy + 8}", color=BLUE))
        o.append(alabel(470, cy + 46, "previous ciphertext", fill=BLUE))
        o.append(arrow(575, cy - 4, 612, cy - 4)); o.append(EK(612, cy - 20)); o.append(arrow(670, cy - 4, 706, cy - 4))
        o.append(box(706, cy - 20, 150, 32, "C2 ≠ C1  — no leak", fill=GREEN, stroke="#15803d", tc="#fff", size=12))
        return "".join(o)

    def gcm(y0):
        o = []; cy = y0 + 92
        o.append(box(44, cy - 16, 120, 32, "nonce + counter", size=11))
        o.append(arrow(164, cy, 200, cy)); o.append(EK(200, cy - 16)); o.append(arrow(258, cy, 300, cy))
        o.append(text(279, cy - 6, "keystream", size=9.5, fill=MUTED))
        o.append(box(300, cy - 58, 74, 26, "P1", size=11))
        o.append(xor(330, cy)); o.append(arrow(330, cy - 32, 330, cy - 16))
        o.append(arrow(345, cy, 470, cy))
        o.append(box(470, cy - 18, 150, 36, "C1  +  auth tag", fill=GREEN, stroke="#15803d", tc="#fff", size=12))
        o.append(text(680, cy - 4, "nonce per message →", size=10.5, fill=MUTED, anchor="start"))
        o.append(text(680, cy + 12, "no repeats; tag detects tampering", size=10.5, fill=MUTED, anchor="start"))
        return "".join(o)
    b.append(lane(62, "AES-ECB  —  the plaintext block is the only input", ecb))
    b.append(lane(224, "AES-CBC  —  each block is XORed with the previous ciphertext (random IV)", cbc))
    b.append(lane(386, "AES-GCM  —  encrypt a per-message nonce+counter, XOR into the plaintext, then authenticate", gcm))
    return svg(W, 552, "Why only ECB leaks structure", "".join(b),
               subtitle="same plaintext blocks under the same key — only ECB maps them to the same ciphertext")

for name, fn in [("modes-ecb-cbc-gcm", d1), ("taxonomy", d2), ("vector3-byte-at-a-time", d3), ("vector4-cut-and-paste", d4)]:
    (OUT / f"{name}.svg").write_text(fn())
    print("wrote", name + ".svg")
