"""Generate the four hand-authored diagrams embedded in docs/index.html.

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
    r1 = (70, 150, 340, 68)
    r2 = (490, 150, 340, 68)
    b.append(box(*r1, "Root cause 1 — Determinism\nsame plaintext block → same ciphertext block,\nat any position, in any message",
                 fill=NAVY, stroke="#0d1b2a", tc="#fff", size=12.5))
    b.append(box(*r2, "Root cause 2 — No authentication\nnothing detects a ciphertext that was\naltered or reassembled",
                 fill=NAVY, stroke="#0d1b2a", tc="#fff", size=12.5))
    b.append(arrow(W / 2, 106, r1[0] + r1[2] / 2, r1[1] - 2))
    b.append(arrow(W / 2, 106, r2[0] + r2[2] / 2, r2[1] - 2))
    vy, vh = 268, 66
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
    r1c, r2c = r1[0] + r1[2] / 2, r2[0] + r2[2] / 2
    v4cx = vs[3][0] + vs[3][1] / 2
    for x, w, *_ in vs[:3]:
        b.append(arrow(r1c, r1[1] + r1[3], x + w / 2, vy - 2))
    b.append(arrow(r2c, r2[1] + r2[3], v4cx, vy - 2))
    # Vector 4 needs BOTH causes: determinism is what makes the moved block decrypt
    # the same way at its new position. Dashed to mark the second dependency.
    b.append(path(f"M {r1c} {r1[1] + r1[3]} C {r1c} {r1[1] + r1[3] + 34}, {v4cx - 120} {vy - 30}, {v4cx - 26} {vy - 2}", dashed=True))
    b.append(alabel((r1c + v4cx) / 2 + 40, vy - 26, "Vector 4 needs determinism too"))
    b.append(text(W / 2, 372, "Scope: educational analysis of ECB's failure modes; every vector here is demonstrated only against the local in-page oracle in this project.",
                  size=10.5, fill=MUTED))
    return svg(W, 388, "ECB's two root causes and four attack vectors", "".join(b),
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

    def swatch(x, y, kind, lbl):
        if kind == "known":
            r = f'<rect x="{x}" y="{y}" width="15" height="15" rx="3" fill="#fef3c7" stroke="{AMBER}" stroke-width="1.2"/>'
        elif kind == "unknown":
            r = f'<rect x="{x}" y="{y}" width="15" height="15" rx="3" fill="#ede9fe" stroke="{PURPLE}" stroke-width="1.2"/>'
        else:
            r = f'<rect class="cellA" x="{x}" y="{y}" width="15" height="15" rx="3" stroke-width="1.2"/>'
        return r + text(x + 21, y + 12, lbl, size=10.5, fill=MUTED, anchor="start", weight="500"), x + 21 + len(lbl) * 5.5 + 22

    def legend(y, items):
        out, x = [], 48
        for kind, lbl in items:
            s, x = swatch(x, y, kind, lbl)
            out.append(s)
        return "".join(out)

    def step(y0, title, cap1, tcells, cap2, pcells):
        o = [panel(30, y0, W - 60, 168),
             text(48, y0 + 24, title, size=13, fill=INK, weight="700", anchor="start"),
             text(bx, y0 + 46, cap1, size=11.5, fill=MUTED, anchor="start"),
             block_cells(bx, y0 + 54, tcells),
             text(bx, y0 + 110, cap2, size=11.5, fill=MUTED, anchor="start"),
             block_cells(bx, y0 + 118, pcells)]
        return "".join(o)
    A = ("A", "A")
    b.append(legend(114, [("a", "A  =  attacker-chosen filler byte"),
                          ("known", "S0, S1  =  secret byte held by the oracle"),
                          ("unknown", "?  =  candidate the attacker is trying")]))
    b.append(step(140, "Step 1 · recover secret byte 0  —  send 15 filler bytes",
                  "TARGET  ·  encrypt these 16 bytes, keep ciphertext block 0", [A] * 15 + [("S0", "known")],
                  "PROBE  ·  try candidate = 0..255 in the last slot — block matches when ? = S0", [A] * 15 + [("?", "unknown")]))
    b.append(text(W / 2, 328, "▼   shift the filler down by one byte", size=12, fill=MUTED, weight="600"))
    b.append(step(342, "Step 2 · recover secret byte 1  —  send 14 filler bytes",
                  "TARGET  ·  S0 is already known from step 1", [A] * 14 + [("S0", "known"), ("S1", "known")],
                  "PROBE  ·  match now reveals S1 — then shift and repeat for every byte", [A] * 14 + [("S0", "known"), ("?", "unknown")]))
    b.append(text(W / 2, 530, "▼   repeat for each byte", size=12, fill=MUTED, weight="600"))
    # Cost: each position costs 1 query to capture the target block plus up to 256
    # to find the byte — 257, not 256. Detecting the block size and the secret
    # length costs at most 34 more. Keep these numbers in step with docs/index.html;
    # test/docs-claims.test.mjs fails if they drift.
    b.append(box(W / 2 - 300, 544, 600, 74,
                 "Full secret recovered without ever holding the key\n"
                 "≤ 257 × L oracle queries for an L-byte secret, plus ≤ 34 to size it up\n"
                 "≈ 129 × L on average; ≈ 96 × L for a printable-ASCII secret",
                 fill=GREEN, stroke="#15803d", tc="#fff", size=13, lh=17))
    b.append(text(W / 2, 640, "Scope: run only against a local demonstration oracle (attacks.mjs makeSuffixOracle), never a third-party service.",
                  size=10.5, fill=MUTED))
    return svg(W, 656, "Vector 3 — chosen-plaintext byte-at-a-time recovery", "".join(b))

# ---------------- Diagram 4: cut-and-paste ----------------
def d4():
    b = []
    bw, bh = 205, 46
    x0 = (W - 4 * bw) / 2  # 4 columns: the donor token really is 4 blocks long

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
                  [("email=xxxxxxxxxx", "n"), ("admin + padding", "admin"), ("&uid=1000&role=u", "n"), ("ser + padding", "n")])
    bb, _ = tokrow(yB, "Base token  —  attacker email = ‘aaaaaaaaaaa’ (aligns role= to a block boundary)",
                   [("email=aaaaaaaaaa", "n"), ("a&uid=1000&role=", "n"), ("user + padding", "drop")])
    ff, fxc = tokrow(yF, "Forged token  —  Base blocks 0–1 + Donor’s admin block",
                     [("email=aaaaaaaaaa", "n"), ("a&uid=1000&role=", "n"), ("admin + padding", "admin")])
    b += [d, bb, ff]
    donor_admin_cx = x0 + 1 * bw + (bw - 6) / 2
    forged_admin_cx = fxc[2]
    # Route the splice orthogonally through the channel right of the base row's
    # blocks (the base token is 3 blocks, so column 3 is free) — a direct curve
    # would cross the "user + padding" block it is supposed to be replacing.
    gut, yTop, yBot = x0 + 3 * bw + 40, yD + bh + 14, yF - 16
    b.append(path(f"M {donor_admin_cx} {yD + bh} L {donor_admin_cx} {yTop} L {gut} {yTop} "
                  f"L {gut} {yBot} L {forged_admin_cx} {yBot} L {forged_admin_cx} {yF - 2}", dashed=True, color=RED))
    b.append(alabel((donor_admin_cx + gut) / 2, yTop - 4, "copy this ciphertext block", fill=RED))
    b.append(alabel(x0 + 2 * bw + (bw - 6) / 2, yB + bh + 16, "dropped before splicing", fill=GRAY))
    b.append(box(W / 2 - 250, 392, 500, 42, "Decrypts to role=admin  —  server accepts it; no integrity check to fail",
                 fill=GREEN, stroke="#15803d", tc="#fff", size=13))
    b.append(text(W / 2, 456, "Scope: ProfileService is a self-contained local stand-in; the target key stays in-process, no external system involved.",
                  size=10.5, fill=MUTED))
    return svg(W, 472, "Vector 4 — block cut-and-paste privilege escalation", "".join(b))

# ---------------- Diagram 1: three modes (concrete block comparison) ----------------
def d1():
    b = []
    b.append(text(W / 2, 80, "Take two identical 16-byte plaintext blocks and encrypt them under one key", size=13, fill=MUTED))
    pw, ph, py = 80, 46, 92
    px1, px2 = W / 2 - pw - 24, W / 2 + 24
    b.append(box(px1, py, pw, ph, "P₁", fill="#3b82f6", stroke="#1d4ed8", tc="#fff", size=15, weight="700"))
    b.append(box(px2, py, pw, ph, "P₂", fill="#3b82f6", stroke="#1d4ed8", tc="#fff", size=15, weight="700"))
    b.append(text(W / 2, py + ph / 2 + 7, "=", size=24, fill="#1d4ed8", weight="800"))
    b.append(text(W / 2, py + ph + 16, "identical input", size=11, fill=MUTED, weight="600"))
    b.append(text(W / 2, 170, "↓   encrypted three ways   ↓", size=12, fill=MUTED, weight="600"))

    def moderow(y0, name, caption, c1, c2, same, tagcolor, tagtext):
        o = [panel(24, y0, W - 48, 96)]
        o.append(f'<rect x="44" y="{y0 + 18}" width="120" height="30" rx="15" fill="{NAVY}"/>')
        o.append(text(44 + 60, y0 + 38, name, size=13, fill="#fff", weight="700"))
        o.append(text(44, y0 + 56, caption, size=11.5, fill=MUTED, anchor="start", lh=13.5))
        ow, oh = 82, 46
        ox2 = W - 48 - ow - 10
        ox1 = ox2 - ow - 46
        o.append(box(ox1, y0 + 22, ow, oh, "C₁", fill=c1, stroke="#0000001f", tc="#fff", size=14, weight="700"))
        o.append(box(ox2, y0 + 22, ow, oh, "C₂", fill=c2, stroke="#0000001f", tc="#fff", size=14, weight="700"))
        o.append(text((ox1 + ow + ox2) / 2, y0 + 22 + oh / 2 + 8, "=" if same else "≠", size=24, fill=tagcolor, weight="800"))
        o.append(text((ox1 + ox2 + ow) / 2, y0 + 86, tagtext, size=11, fill=tagcolor, weight="700"))
        return "".join(o)

    b.append(moderow(184, "AES-ECB",
        "Feeds each plaintext block straight into AES with nothing\nmixed in — same block in, same block out, at any position\nand in every message encrypted under that key.",
        "#dc2626", "#dc2626", True, RED, "C₁ = C₂  →  the pattern leaks"))
    # The first CBC block has no preceding ciphertext — it is XORed with the IV,
    # and a fresh IV per message is what stops the repeat across messages. Saying
    # only "XORs with the previous ciphertext" is wrong for P₁, which is drawn here.
    b.append(moderow(292, "AES-CBC",
        "XORs each block with the previous ciphertext, and the first\nwith a fresh random IV per message — so identical blocks\nnever enter AES the same way twice.",
        "#0ea5e9", "#f59e0b", False, GREEN, "C₁ ≠ C₂  →  no leak"))
    b.append(moderow(400, "AES-GCM",
        "XORs the plaintext with a keystream derived from a fresh\nper-message nonce, then authenticates the result — the\nplaintext never enters AES directly at all.",
        "#8b5cf6", "#10b981", False, GREEN, "C₁ ≠ C₂  →  no leak"))
    b.append(text(W / 2, 524, "CBC and GCM avoid the repeat only while the IV / nonce is fresh for every message under the key; reuse one and the leak comes back.",
                  size=10.5, fill=MUTED))
    return svg(W, 540, "Why only ECB leaks structure", "".join(b),
               subtitle="the same identical pair, three modes — only ECB hands back an identical pair")

for name, fn in [("modes-ecb-cbc-gcm", d1), ("taxonomy", d2), ("vector3-byte-at-a-time", d3), ("vector4-cut-and-paste", d4)]:
    # Trailing newline so the committed file agrees with the end-of-file-fixer
    # pre-commit hook; without it the hook and this generator overwrite each
    # other and the byte-identical regeneration check never holds.
    (OUT / f"{name}.svg").write_text(fn() + "\n")
    print("wrote", name + ".svg")
