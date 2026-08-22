import pathlib
OUT = pathlib.Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

SANS = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
INK, MUTED = "#0f172a", "#475569"
CARD, BORDER = "#ffffff", "#e2e8f0"
NEU_F, NEU_S = "#f1f5f9", "#cbd5e1"
NAVY = "#1f3a5f"
RED, GREEN, PURPLE, AMBER, GRAY = "#dc2626", "#16a34a", "#6d28d9", "#b45309", "#64748b"
BLUE = "#2563eb"
ARROW = "#94a3b8"

def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def text(x,y,s,size=13,fill=INK,anchor="middle",weight="400",mono=False,lh=15):
    font = MONO if mono else SANS
    lines = s.split("\n")
    parts=[f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">']
    for i,ln in enumerate(lines):
        dy = 0 if i==0 else lh
        parts.append(f'<tspan x="{x}" dy="{dy}">{esc(ln)}</tspan>')
    parts.append('</text>')
    return "".join(parts)

def box(x,y,w,h,label,fill=NEU_F,stroke=NEU_S,tc=INK,mono=False,rx=9,size=13,weight="600",lh=15,sw=1.5):
    n=len(label.split("\n"))
    cx=x+w/2; cy=y+h/2
    first = cy - (n-1)*lh/2 + size/3
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
            + text(cx, first, label, size=size, fill=tc, mono=mono, weight=weight, lh=lh))

def arrow(x1,y1,x2,y2,dashed=False,color=ARROW,sw=2):
    da = ' stroke-dasharray="6 5"' if dashed else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{da} marker-end="url(#arw)"/>'

def path(d,dashed=False,color=ARROW,sw=2):
    da=' stroke-dasharray="6 5"' if dashed else ''
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da} marker-end="url(#arw)"/>'

def alabel(x,y,s,size=11,fill=MUTED):
    w=len(s)*size*0.56+10
    return (f'<rect x="{x-w/2}" y="{y-size+2}" width="{w}" height="{size+6}" rx="4" fill="#ffffff" opacity="0.95"/>'
            + text(x,y+3,s,size=size,fill=fill,weight="500"))

def svg(w,h,title,body,subtitle=None):
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{SANS}">'
            f'<defs><marker id="arw" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">'
            f'<path d="M0,0 L8,3 L0,6 z" fill="{ARROW}"/></marker></defs>'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{CARD}" stroke="{BORDER}" stroke-width="2"/>'
            + text(w/2, 32, title, size=17, fill=INK, weight="700"))
    if subtitle:
        head += text(w/2, 52, subtitle, size=12, fill=MUTED)
    return head + body + '</svg>'

W = 900

# ---------------- Diagram 2: taxonomy ----------------
def d2():
    b=[]
    # ECB root
    b.append(box(W/2-80, 62, 160, 44, "AES-ECB", fill=NAVY, stroke="#0d1b2a", tc="#fff", size=15, weight="700"))
    # root causes
    r1=(90,150,320,58); r2=(490,150,320,58)
    b.append(box(*r1, "Root cause 1 — Determinism\nequal plaintext block → equal ciphertext block", fill=NAVY, stroke="#0d1b2a", tc="#fff", size=12.5, weight="600"))
    b.append(box(*r2, "Root cause 2 — No integrity / no chaining\nblocks independent and unauthenticated", fill=NAVY, stroke="#0d1b2a", tc="#fff", size=12.5, weight="600"))
    b.append(arrow(W/2, 106, r1[0]+r1[2]/2, r1[1]-2))
    b.append(arrow(W/2, 106, r2[0]+r2[2]/2, r2[1]-2))
    # vectors
    vy=258; vh=66
    vs=[
        (30,190,"Vector 1","Pattern & structure leakage","passive",BLUE),
        (232,190,"Vector 2","Equality & frequency inference","passive / statistical",BLUE),
        (434,180,"Vector 3","Byte-at-a-time recovery","active oracle",BLUE),
        (640,230,"Vector 4","Block malleability / cut-and-paste","active splice",AMBER),
    ]
    for x,w,vt,desc,mode,ac in vs:
        b.append(f'<rect x="{x}" y="{vy}" width="{w}" height="{vh}" rx="9" fill="{NEU_F}" stroke="{NEU_S}" stroke-width="1.5"/>')
        b.append(f'<rect x="{x}" y="{vy}" width="6" height="{vh}" rx="3" fill="{ac}"/>')
        cx=x+w/2
        b.append(text(cx, vy+22, vt, size=13, fill=INK, weight="700"))
        b.append(text(cx, vy+40, desc, size=11.5, fill=INK))
        b.append(text(cx, vy+56, mode, size=11, fill=MUTED, weight="500"))
    # connectors R1->V1,V2,V3 ; R2->V4
    r1c=r1[0]+r1[2]/2
    for x,w,*_ in vs[:3]:
        b.append(arrow(r1c, r1[1]+r1[3], x+w/2, vy-2))
    b.append(arrow(r2[0]+r2[2]/2, r2[1]+r2[3], vs[3][0]+vs[3][1]/2, vy-2))
    return svg(W, 348, "ECB's two root causes and four attack vectors",
               "".join(b),
               subtitle="every vector follows from one or both root causes — there is no third")

# ---------------- byte-cell block helper ----------------
def block_cells(x, y, cells, cw=34, ch=30):
    # cells: list of (label, kind) kind in neutral/known/unknown
    out=[]
    palette={"A":(NEU_F,NEU_S,MUTED),"known":("#fef3c7",AMBER,"#92400e"),
             "unknown":("#ede9fe",PURPLE,"#5b21b6")}
    for i,(lbl,kind) in enumerate(cells):
        f,s,tc=palette.get(kind,palette["A"])
        cx=x+i*cw
        out.append(f'<rect x="{cx}" y="{y}" width="{cw}" height="{ch}" fill="{f}" stroke="{s}" stroke-width="1.2"/>')
        out.append(text(cx+cw/2, y+ch/2+4.5, lbl, size=12, fill=tc, mono=True, weight="700"))
    return "".join(out)

# ---------------- Diagram 3: byte-at-a-time ----------------
def d3():
    b=[]
    b.append(box(40, 62, W-80, 40, "Oracle:   C = AES-ECB( attacker_input ‖ secret ),   fixed key — never revealed",
                 fill=NAVY, stroke="#0d1b2a", tc="#fff", size=13, weight="600"))
    bx = (W-16*34)/2
    def step(y0, title, cap1, tcells, cap2, pcells):
        o=[f'<rect x="30" y="{y0}" width="{W-60}" height="168" rx="10" fill="#f8fafc" stroke="{BORDER}" stroke-width="1.5"/>']
        o.append(text(48, y0+24, title, size=13, fill=INK, weight="700", anchor="start"))
        o.append(text(bx, y0+46, cap1, size=11.5, fill=MUTED, anchor="start"))
        o.append(block_cells(bx, y0+54, tcells))
        o.append(text(bx, y0+110, cap2, size=11.5, fill=MUTED, anchor="start"))
        o.append(block_cells(bx, y0+118, pcells))
        return "".join(o)
    A=("A","A")
    b.append(step(118, "Step 1 · recover secret byte 0  —  send 15 filler bytes",
        "TARGET  ·  encrypt these 16 bytes, keep ciphertext block 0",
        [A]*15+[("S0","known")],
        "PROBE  ·  try candidate = 0..255 in the last slot — block matches when ? = S0",
        [A]*15+[("?","unknown")]))
    b.append(text(W/2, 306, "▼   shift the filler down by one byte", size=12, fill=MUTED, weight="600"))
    b.append(step(320, "Step 2 · recover secret byte 1  —  send 14 filler bytes",
        "TARGET  ·  S0 is already known from step 1",
        [A]*14+[("S0","known"),("S1","known")],
        "PROBE  ·  match now reveals S1 — then shift and repeat for every byte",
        [A]*14+[("S0","known"),("?","unknown")]))
    b.append(text(W/2, 508, "▼   repeat for each byte", size=12, fill=MUTED, weight="600"))
    b.append(box(W/2-240, 522, 480, 42, "Full secret recovered in ≈ 256 × L queries — the key is never needed",
                 fill=GREEN, stroke="#15803d", tc="#fff", size=13, weight="600"))
    b.append(text(W/2, 584, "Scope: run only against a local demonstration oracle (ecb_lab.oracle_attack.make_suffix_oracle), never a third-party service.",
                  size=10.5, fill=MUTED))
    return svg(W, 600, "Vector 3 — chosen-plaintext byte-at-a-time recovery", "".join(b))

# ---------------- Diagram 4: cut-and-paste ----------------
def d4():
    b=[]
    bw=254; bh=46; x0=(W-3*bw)/2
    def tokrow(y, label, blocks, note_color=INK):
        o=[text(x0, y-10, label, size=12.5, fill=INK, weight="700", anchor="start")]
        for i,(txt,kind) in enumerate(blocks):
            f,s,tc=(NEU_F,NEU_S,INK)
            if kind=="admin": f,s,tc=("#fee2e2",RED,"#991b1b")
            if kind=="drop":  f,s,tc=("#f1f5f9",GRAY,GRAY)
            x=x0+i*bw
            o.append(f'<rect x="{x}" y="{y}" width="{bw-6}" height="{bh}" rx="8" fill="{f}" stroke="{s}" stroke-width="1.6"/>')
            o.append(text(x+(bw-6)/2, y+18, f"block {i}", size=10, fill=MUTED, weight="600"))
            o.append(text(x+(bw-6)/2, y+35, txt, size=12, fill=tc, mono=True, weight="600"))
            if kind=="drop":
                o.append(f'<line x1="{x+8}" y1="{y+bh-6}" x2="{x+bw-14}" y2="{y+6}" stroke="{GRAY}" stroke-width="1.5" stroke-dasharray="4 3"/>')
        return "".join(o), [x0+i*bw+(bw-6)/2 for i in range(len(blocks))]
    yD, yB, yF = 88, 196, 322
    d,_ = tokrow(yD, "Donor token  —  attacker email = ‘xxxxxxxxxx’ + admin-padding",
                 [("email=xxxxxxxxxx","n"),("admin + padding","admin"),("&uid=1000&role=user …","n")])
    bb,bxc = tokrow(yB, "Base token  —  attacker email = ‘aaaaaaaaaaa’ (aligns role= to a block boundary)",
                 [("email=aaaaaaaaaa","n"),("a&uid=1000&role=","n"),("user + padding","drop")])
    ff,fxc = tokrow(yF, "Forged token  —  Base blocks 0–1 + Donor’s admin block",
                 [("email=aaaaaaaaaa","n"),("a&uid=1000&role=","n"),("admin + padding","admin")])
    b += [d,bb,ff]
    # donor admin block center:
    donor_admin_cx = x0+1*bw+(bw-6)/2
    forged_admin_cx = fxc[2]
    # copy arrow: donor block1 bottom -> forged block2 top (curved)
    b.append(path(f"M {donor_admin_cx} {yD+bh} C {donor_admin_cx} {yD+bh+70}, {forged_admin_cx} {yF-70}, {forged_admin_cx} {yF-2}", dashed=True, color=RED))
    b.append(alabel((donor_admin_cx+forged_admin_cx)/2, yD+bh+22, "copy this ciphertext block", fill=RED))
    # drop marker on base block2
    b.append(alabel(bxc[2], yB+bh+16, "dropped before splicing", fill=GRAY))
    # result
    b.append(box(W/2-250, 392, 500, 42, "Decrypts to role=admin  —  server accepts it; no integrity check to fail",
                 fill=GREEN, stroke="#15803d", tc="#fff", size=13, weight="600"))
    b.append(text(W/2, 456, "Scope: ProfileService is a self-contained local stand-in; the target key stays in-process, no external system involved.",
                  size=10.5, fill=MUTED))
    return svg(W, 472, "Vector 4 — block cut-and-paste privilege escalation", "".join(b))

# ---------------- Diagram 1: three modes ----------------
def d1():
    b=[]
    def lane(y0, title, sub_ok, draw):
        o=[f'<rect x="24" y="{y0}" width="{W-48}" height="150" rx="10" fill="#f8fafc" stroke="{BORDER}" stroke-width="1.5"/>',
           text(40, y0+24, title, size=13, fill=INK, weight="700", anchor="start")]
        o.append(draw(y0))
        return "".join(o)
    EK=lambda x,y,w=58,h=32: box(x,y,w,h,"Eₖ",fill="#e0e7ff",stroke="#6366f1",tc="#3730a3",size=14,weight="700",rx=7)
    def xor(cx,cy,r=15):
        return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{MUTED}" stroke-width="1.8"/>'
                +text(cx,cy+5,"⊕",size=16,fill=MUTED,weight="700"))
    # ECB lane
    def ecb(y0):
        o=[]
        ry1=y0+58; ry2=y0+106; h=32
        o.append(box(48,ry1-16,74,h,"P1",fill=NEU_F,stroke=NEU_S)); o.append(arrow(122,ry1,168,ry1))
        o.append(EK(168,ry1-16)); o.append(arrow(226,ry1,272,ry1))
        o.append(box(272,ry1-16,74,h,"C1",fill=NEU_F,stroke=NEU_S))
        o.append(box(48,ry2-16,74,h,"P2 = P1",fill=NEU_F,stroke=NEU_S,size=11)); o.append(arrow(122,ry2,168,ry2))
        o.append(EK(168,ry2-16)); o.append(arrow(226,ry2,272,ry2))
        o.append(box(272,ry2-16,210,h,"C2 = C1  — structure leaks",fill=RED,stroke="#991b1b",tc="#fff",size=12))
        # equality brace between C1 and C2
        o.append(f'<path d="M 500 {ry1} C 528 {ry1}, 528 {ry2}, 500 {ry2}" fill="none" stroke="{RED}" stroke-width="1.6"/>')
        o.append(text(548,(ry1+ry2)/2+4,"identical",size=11,fill=RED,weight="700"))
        o.append(text(548,(ry1+ry2)/2+20,"in → identical out",size=10.5,fill=MUTED))
        return "".join(o)
    # CBC lane
    def cbc(y0):
        o=[]; cy=y0+92
        o.append(box(44,cy-52,84,26,"random IV",fill=NEU_F,stroke=NEU_S,size=10.5))
        o.append(box(44,cy-10,74,26,"P1",fill=NEU_F,stroke=NEU_S,size=11))
        o.append(arrow(128,cy-39,169,cy-10)); o.append(arrow(118,cy+3,169,cy-4))
        o.append(xor(184,cy-4)); o.append(arrow(199,cy-4,236,cy-4))
        o.append(EK(236,cy-20)); o.append(arrow(294,cy-4,330,cy-4))
        o.append(box(330,cy-20,74,32,"C1",fill=NEU_F,stroke=NEU_S))
        # feedback C1 -> xor2
        o.append(box(470,cy-52,84,26,"P2 = P1",fill=NEU_F,stroke=NEU_S,size=10.5))
        o.append(xor(560,cy-4)); o.append(arrow(544,cy-39,560,cy-19))
        o.append(path(f"M 404 {cy-4} C 430 {cy-4}, 430 {cy+34}, 545 {cy+34} L 545 {cy+8} L 552 {cy+8}",color=BLUE))
        o.append(alabel(470,cy+46,"previous ciphertext",fill=BLUE))
        o.append(arrow(575,cy-4,612,cy-4)); o.append(EK(612,cy-20)); o.append(arrow(670,cy-4,706,cy-4))
        o.append(box(706,cy-20,150,32,"C2 ≠ C1  — no leak",fill=GREEN,stroke="#15803d",tc="#fff",size=12))
        return "".join(o)
    # GCM lane
    def gcm(y0):
        o=[]; cy=y0+92
        o.append(box(44,cy-16,120,32,"nonce + counter",fill=NEU_F,stroke=NEU_S,size=11))
        o.append(arrow(164,cy,200,cy)); o.append(EK(200,cy-16)); o.append(arrow(258,cy,300,cy))
        o.append(text(279,cy-6,"keystream",size=9.5,fill=MUTED))
        o.append(box(300,cy-58,74,26,"P1",fill=NEU_F,stroke=NEU_S,size=11))
        o.append(xor(330,cy)); o.append(arrow(330,cy-32,330,cy-16))
        o.append(arrow(345,cy,470,cy))
        o.append(box(470,cy-18,150,36,"C1  +  auth tag",fill=GREEN,stroke="#15803d",tc="#fff",size=12))
        o.append(text(680,cy-4,"nonce per message →",size=10.5,fill=MUTED,anchor="start"))
        o.append(text(680,cy+12,"no repeats; tag detects tampering",size=10.5,fill=MUTED,anchor="start"))
        return "".join(o)
    b.append(lane(62,  "AES-ECB  —  the plaintext block is the only input", False, ecb))
    b.append(lane(224, "AES-CBC  —  each block is XORed with the previous ciphertext (random IV)", True, cbc))
    b.append(lane(386, "AES-GCM  —  encrypt a per-message nonce+counter, XOR into the plaintext, then authenticate", True, gcm))
    return svg(W, 552, "Why only ECB leaks structure",
               "".join(b),
               subtitle="same plaintext blocks under the same key — only ECB maps them to the same ciphertext")

for name,fn in [("modes-ecb-cbc-gcm",d1),("taxonomy",d2),("vector3-byte-at-a-time",d3),("vector4-cut-and-paste",d4)]:
    (OUT/f"{name}.svg").write_text(fn())
    print("wrote", name+".svg", len((OUT/f'{name}.svg').read_text()), "bytes")
