#!/usr/bin/env python3
"""Bina laman kursus 1503250 daripada fail _src/bab/babNN.json.
สร้างเว็บไซต์ทั้งหมดจากไฟล์บทเรียน _src/bab/babNN.json

    python3 _src/build.py      # bina HTML · สร้างหน้าเว็บ
    python3 _src/pdf.py        # bina pdf/bab-NN.pdf daripada halaman bab · สร้าง PDF
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
GC = "bm-perniagaan"  # GoatCounter

# Bab yang jawapannya sudah dibuka (selepas kelas diajar)
# บทที่เปิดเฉลยแล้ว (หลังสอนคาบนั้น) เพิ่มเลขบทลงในรายการนี้ เช่น [1, 2, 3]
BUKA_JAWAPAN = []

KURSUS = {
    "kod": "1503250", "ms": "Bahasa Melayu untuk Perniagaan", "th": "ภาษามลายูเพื่อธุรกิจ",
    "sem": "Semester 2/2569", "semTh": "ภาคเรียนที่ 2/2569",
}
HALAMAN = [
    ("index.html", "Laman Utama", "หน้าแรก"),
    ("jadual.html", "Jadual 15 Kelas", "แผนการสอน"),
    ("pelajaran.html", "Pelajaran", "บทเรียน 14 บท"),
    ("penilaian.html", "Penilaian", "การวัดผล"),
    ("dokumen.html", "Muat Turun", "ดาวน์โหลด"),
]

# Bahagian yang tidak dipaparkan kepada pelajar (bahan guru)
# ส่วนสำหรับผู้สอน ไม่แสดงบนเว็บและไม่ใส่ในไฟล์ฉบับนิสิต
SEMBUNYI = ("Ujian Pra", "Skrip Guru", "Aktiviti Pembelajaran")

# Kelas → bab (Kelas 8 = peperiksaan pertengahan semester)
def kelas_bab(n):
    return n if n <= 7 else n + 1


def esc(s):
    return html.escape(str(s), quote=False)


def rich(s):
    s = esc(s)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def is_thai(s):
    return bool(re.search(r"[฀-๿]", s or ""))


def muat_bab():
    bab = []
    for f in sorted((SRC / "bab").glob("bab*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        d["no"] = int(f.stem[3:])
        d["kelas"] = kelas_bab(d["no"])
        meta = {re.sub(r"\*", "", k): v for k, v in d.get("meta", [])}
        d["clo"] = meta.get("CLO", ["", ""])[0]
        bab.append(d)
    return bab


def tersembunyi(sec):
    return any(k in sec["ms"] for k in SEMBUNYI)


# ---------- blok → HTML ----------
def sel(c, head=False):
    tag = "th" if head else "td"
    if isinstance(c, list):
        if len(c) == 3:  # [ms, pilihan, th]
            inner = f'<span class="ms">{rich(c[0])}</span><span class="ms">{rich(c[1])}</span><span class="th">{rich(c[2])}</span>'
        else:
            inner = f'<span class="ms">{rich(c[0])}</span>' + "".join(
                f'<span class="th">{rich(x)}</span>' for x in c[1:] if x)
    else:
        c = str(c)
        if head and " · " in c:
            a, b = c.split(" · ", 1)
            inner = f'{rich(a)}<small>{rich(b)}</small>'
        else:
            inner = f'<span class="{"th" if is_thai(c) and not head else "ms"}">{rich(c)}</span>' if c else ""
    return f"<{tag}>{inner}</{tag}>"


TUTUP = ('<div class="jawapan-tutup"><span class="ms">Jawapan akan dibuka selepas kelas.</span>'
         '<span class="th">เฉลยจะเปิดหลังเรียนคาบนี้</span></div>')


def blok(b, buka=True):
    t = b["t"]
    if t == "bi":
        return f'<div class="bi"><p class="ms">{rich(b["ms"])}</p><p class="th">{rich(b["th"])}</p></div>'
    if t == "h2":
        return f'<h3><span class="ms">{rich(b["ms"])}</span><span class="th">{rich(b["th"])}</span></h3>'
    if t == "p":
        txt = b["text"]
        if txt.startswith("**Jawapan"):
            if not buka:
                return TUTUP
            label, _, rest = txt.partition(":**")
            return ('<details class="jawapan"><summary>Tunjuk jawapan · ดูเฉลย</summary>'
                    f'<p>{rich(rest.strip())}</p></details>')
        return f"<p>{rich(txt)}</p>"
    if t == "bullets":
        li = []
        for it in b["items"]:
            if isinstance(it, list):
                li.append(f'<li><span class="ms">{rich(it[0])}</span><span class="th">{rich(it[1])}</span></li>')
            else:
                li.append(f'<li class="{"th" if is_thai(it) else ""}">{rich(it)}</li>')
        return "<ul>" + "".join(li) + "</ul>"
    if t == "table":
        h = ""
        if b.get("head"):
            h = "<thead><tr>" + "".join(sel(c, True) for c in b["head"]) + "</tr></thead>"
        rows = "".join("<tr>" + "".join(sel(c) for c in r) + "</tr>" for r in b["rows"])
        return f'<div class="jadual-bungkus"><table>{h}<tbody>{rows}</tbody></table></div>'
    if t == "box":
        ps = "".join(f'<p class="{"th" if ln[1] else "ms"}">{rich(ln[0])}</p>' for ln in b["lines"])
        return f'<div class="kotak">{ps}</div>'
    if t == "dialog":
        rows = "".join(
            f'<div class="dl"><span class="siapa">{esc(w)}</span><div><span class="ms">{rich(m)}</span>'
            f'<span class="th">{rich(th)}</span></div></div>' for w, m, th in b["lines"])
        return f'<div class="dialog">{rows}</div>'
    return ""  # pagebreak


def seksyen(sec, idx, buka=True):
    # tajuk kecil + blok pertama tidak dipisahkan semasa cetak · หัวข้อย่อยไม่แยกจากเนื้อหาตอนพิมพ์
    bs = [b for b in sec["blocks"] if b["t"] != "pagebreak"]
    parts, i = [], 0
    while i < len(bs):
        if bs[i]["t"] == "h2" and i + 1 < len(bs):
            parts.append(f'<div class="ikat">{blok(bs[i], buka)}{blok(bs[i + 1], buka)}</div>')
            i += 2
        else:
            parts.append(blok(bs[i], buka))
            i += 1
    tajuk = re.sub(r"^\d+\.\s*", "", sec["ms"])
    if re.fullmatch(r"Jawapan", tajuk):
        parts = [TUTUP] if not buka else [
            '<details class="jawapan"><summary>Tunjuk jawapan · ดูเฉลย</summary>' + "".join(parts) + "</details>"]
    h = f'<h2><span class="ms">{idx}. {esc(tajuk)}</span><span class="th">{esc(sec["th"])}</span></h2>'
    # tajuk seksyen + blok pertama diikat · ผูกหัวข้อกับเนื้อหาส่วนแรก
    if parts and parts[0].startswith('<div class="ikat">'):
        isi = parts[0].replace('<div class="ikat">', '<div class="ikat">' + h, 1) + "".join(parts[1:])
    elif parts and len(parts[0]) < 4000:
        isi = f'<div class="ikat">{h}{parts[0]}</div>' + "".join(parts[1:])
    else:
        isi = h + "".join(parts)
    return f'<section class="seksyen" id="s{idx}">{isi}</section>'


# ---------- rangka halaman ----------
LENCANA = ('<svg class="lencana" viewBox="0 0 40 40" aria-hidden="true"><rect x="1.5" y="1.5" width="37" height="37" rx="7" '
           'fill="#1F5D40" stroke="#D4A62A" stroke-width="2"/><path d="M20 8 L31 20 L20 32 L9 20 Z" fill="none" '
           'stroke="#D4A62A" stroke-width="2.2"/><path d="M20 14 L25 20 L20 26 L15 20 Z" fill="#D4A62A"/></svg>')


def halaman(fail, tajuk, isi, aras="", aktif=None, keterangan=""):
    aktif = aktif or fail
    nav = "".join(
        f'<a href="{aras}{f}"{" aria-current=\"page\"" if f == aktif else ""}>{ms}<small>{th}</small></a>'
        for f, ms, th in HALAMAN)
    return f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(tajuk)} · {KURSUS['kod']} {KURSUS['ms']}</title>
<meta name="description" content="{esc(keterangan or 'Laman kursus 1503250 Bahasa Melayu untuk Perniagaan (ภาษามลายูเพื่อธุรกิจ), Universiti Thaksin.')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Sarabun:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{aras}css/gaya.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' rx='7' fill='%231F5D40'/%3E%3Cpath d='M20 8 L31 20 L20 32 L9 20 Z' fill='none' stroke='%23D4A62A' stroke-width='2.4'/%3E%3Cpath d='M20 14 L25 20 L20 26 L15 20 Z' fill='%23D4A62A'/%3E%3C/svg%3E">
</head>
<body>
<a class="lompat" href="#isi">Langkau ke kandungan · ข้ามไปยังเนื้อหา</a>
<header class="kepala"><div class="kepala-dalam">
<a class="jenama" href="{aras}index.html">{LENCANA}<span><span class="jenama-kod">{KURSUS['kod']} · {KURSUS['sem']}</span><span class="jenama-nama">{KURSUS['ms']}</span></span></a>
<button class="togol-nav" type="button" aria-expanded="false" aria-controls="nav-utama">Menu · เมนู</button>
<nav class="nav" id="nav-utama" aria-label="Navigasi utama">{nav}</nav>
</div></header>
<div class="songket" aria-hidden="true"></div>
<main id="isi">
{isi}
</main>
<footer class="kaki"><div class="kaki-dalam">
<div><p class="ms">{KURSUS['kod']} {KURSUS['ms']}</p><p>{KURSUS['th']} · {KURSUS['semTh']}</p><p>Program Bahasa Melayu, Fakulti Kemanusiaan dan Sains Sosial, Universiti Thaksin</p></div>
<div><p class="ms">Pensyarah · อาจารย์ผู้สอน</p><p>ผศ.มูหำหมัด สาแลบิง</p><p><a href="mailto:smuhammad@tsu.ac.th">smuhammad@tsu.ac.th</a></p></div>
<div><p class="ms">Waktu konsultasi · เวลาให้คำปรึกษา</p><p>Rabu 13.00–16.00, bilik 1316</p><p>วันพุธ 13.00–16.00 น. ห้อง 1316</p></div>
</div></footer>
<script src="{aras}js/laman.js"></script>
<script data-goatcounter="https://{GC}.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>
"""


CLO = [
    ("CLO1", "Pengetahuan asas, kosa kata dan budaya perniagaan Malaysia",
     "อธิบายความรู้พื้นฐาน คำศัพท์ และวัฒนธรรมชาวมาเลเซียที่เกี่ยวข้องกับธุรกิจได้"),
    ("CLO2", "Kemahiran mendengar, bertutur dan membaca untuk perniagaan",
     "มีทักษะการใช้ภาษามลายู ฟัง พูด อ่าน เพื่อการสื่อสารในธุรกิจ"),
    ("CLO3", "Menggunakan bahasa dalam pelbagai situasi perniagaan",
     "ฝึกปฏิบัติการใช้ภาษาในสถานการณ์ต่าง ๆ ในธุรกิจได้อย่างเหมาะสม"),
    ("CLO4", "Menghargai komunikasi bahasa Melayu dan berani berkomunikasi",
     "แสดงออกถึงคุณค่าในการสื่อสารภาษามลายู กล้าแสดงออก"),
]
MARKAH = [
    ("CLO1", "Peperiksaan pertengahan dan akhir semester", "สอบข้อเขียนกลางภาคและปลายภาค", 30),
    ("CLO2", "Ujian kemahiran mendengar, bertutur dan membaca", "ทดสอบทักษะฟัง พูด อ่าน (Rubric)", 20),
    ("CLO3", "Main peranan dan simulasi perniagaan", "บทบาทสมมติและการจำลองสถานการณ์ (Performance Rubric)", 20),
    ("CLO4", "Pembentangan individu / kumpulan", "การนำเสนอผลงานรายบุคคล/รายกลุ่ม (Presentation Rubric)", 10),
    ("CLO2–4", "Projek kumpulan komunikasi perniagaan", "โครงงานกลุ่มด้านการสื่อสารทางธุรกิจ (Project Rubric)", 10),
    ("CLO4", "Penyertaan dan tanggungjawab", "การมีส่วนร่วมและความรับผิดชอบในการเรียน", 10),
]


def bar_markah():
    out = []
    for clo, ms, th, n in MARKAH:
        out.append(f'<div class="markah"><div class="markah-teks"><span class="ms">{ms}</span><span class="th">{th} · {clo}</span></div>'
                   f'<div class="markah-bar" role="img" aria-label="{n}%"><span style="width:{n * 100 / 30:.0f}%"></span></div><b>{n}%</b></div>')
    return "".join(out)


def kad_bab(d, aras=""):
    return (f'<a class="kad" href="{aras}bab/{d["no"]:02d}.html"><span class="kad-no">Bab {d["no"]}<small>Kelas {d["kelas"]}</small></span>'
            f'<span class="ms">{esc(d["title_ms"])}</span><span class="th">{esc(d["title_th"])}</span>'
            f'<span class="tag">{esc(d["clo"])}</span></a>')


def bina_html(bab):
    # ---- index ----
    clo_html = "".join(f'<div class="panel"><h3><span class="ms">{k} · {ms}</span></h3><p class="th">{th}</p></div>' for k, ms, th in CLO)
    seterus = "".join(kad_bab(d) for d in bab[:3])
    index = f"""
<section class="wira"><div class="wira-teks">
<p class="kicker">{KURSUS['kod']} · 3 kredit · {KURSUS['sem']}</p>
<h1><span class="ms">Bahasa Melayu untuk Perniagaan</span><span class="th">ภาษามลายูเพื่อธุรกิจ</span></h1>
<p class="ms">Kursus ini untuk pelajar yang belum pernah belajar bahasa Melayu. Dalam 15 kelas, anda belajar menyambut pelanggan, bercakap di telefon, membaca invois, membuat pesanan dan menyelesaikan aduan dalam bahasa Melayu.</p>
<p class="th">วิชานี้ออกแบบสำหรับนิสิตที่ไม่มีพื้นฐานภาษามลายู ใน 15 คาบ นิสิตจะได้ฝึกต้อนรับลูกค้า พูดโทรศัพท์ อ่านใบแจ้งหนี้ สั่งซื้อสินค้า และจัดการข้อร้องเรียนเป็นภาษามลายู จนสามารถจำลองสถานการณ์ธุรกิจได้ด้วยตนเอง</p>
<div class="butang-baris"><a class="butang" href="pelajaran.html">Mula belajar<small>เริ่มเรียนบทที่ 1</small></a>
<a class="butang garis" href="jadual.html">Lihat jadual<small>ดูแผนการสอน 15 คาบ</small></a></div>
</div>
<aside class="atur"><h2><span class="ms">Maklumat Kelas</span><span class="th">ข้อมูลการเรียน</span></h2>
<div class="atur-baris"><b>Khamis</b><div><span class="ms">08.00–12.10 · bilik 17401</span><span class="th">วันพฤหัสบดี คาบ 1–4</span></div></div>
<div class="atur-baris"><b>Pelajar</b><div><span class="ms">Tahun 2, Pengurusan Logistik</span><span class="th">นิสิตชั้นปีที่ 2 วิชาเอกการจัดการโลจิสติกส์</span></div></div>
<div class="atur-baris"><b>Masa</b><div><span class="ms">Teori 2 jam · amali 2 jam seminggu</span><span class="th">ทฤษฎี 2 ชม. ปฏิบัติ 2 ชม. ต่อสัปดาห์</span></div></div>
<div class="atur-baris"><b>Alat</b><div><span class="ms">ClassPoint · Padlet · Kahoot! · Google Forms</span><span class="th">เครื่องมือที่ใช้ในชั้นเรียน</span></div></div>
<div class="atur-baris"><b>Rabu</b><div><span class="ms">Konsultasi 13.00–16.00 · bilik 1316</span><span class="th">วันพุธ เวลาให้คำปรึกษา</span></div></div>
</aside></section>

<section class="bahagian"><h2><span class="ms">Mula di sini</span><span class="th">บทเรียนแรก</span></h2>
<div class="grid-kad">{seterus}</div>
<p class="th lagi"><a href="pelajaran.html">ดูบทเรียนทั้ง 14 บท ›</a></p></section>

<section class="bahagian grid-2">
<div><h2><span class="ms">Hasil Pembelajaran Kursus</span><span class="th">ผลลัพธ์การเรียนรู้ระดับรายวิชา (CLOs)</span></h2>{clo_html}</div>
<div><h2><span class="ms">Pecahan Markah</span><span class="th">สัดส่วนคะแนน</span></h2><div class="panel">{bar_markah()}</div>
<p class="th lagi"><a href="penilaian.html">ดูรายละเอียดการวัดผลและ Rubric ›</a></p></div>
</section>

<section class="bahagian"><h2><span class="ms">Cara belajar dengan laman ini</span><span class="th">วิธีใช้เว็บไซต์นี้</span></h2>
<div class="grid-3">
<div class="panel"><h3><span class="ms">1 · Sebelum kelas</span></h3><p class="th">อ่านคำศัพท์และบทสนทนาของบทที่จะเรียนล่วงหน้า 10–15 นาที</p></div>
<div class="panel"><h3><span class="ms">2 · Semasa kelas</span></h3><p class="th">เปิดบทเรียนในโทรศัพท์ ใช้ตารางคำศัพท์และบทสนทนาประกอบกิจกรรม</p></div>
<div class="panel"><h3><span class="ms">3 · Selepas kelas</span></h3><p class="th">ทำแบบฝึกหัด กด "ซ่อนคำแปล" เพื่อทดสอบตัวเอง แล้วกด "ดูเฉลย" ตรวจคำตอบ (เฉลยเปิดหลังเรียนคาบนั้น)</p></div>
</div></section>
"""
    (ROOT / "index.html").write_text(halaman("index.html", "Laman Utama", index), encoding="utf-8")

    # ---- jadual ----
    by_k = {d["kelas"]: d for d in bab}
    rows = []
    for k in range(1, 16):
        if k == 8:
            rows.append('<tr class="ujian"><td>8</td><td><span class="ms"><strong>Peperiksaan Pertengahan Semester</strong></span>'
                        '<span class="th">สอบกลางภาค (เนื้อหาคาบที่ 1–7) ข้อเขียนและสอบปากเปล่า ฟัง–พูด</span></td><td>CLO1, CLO2</td><td>–</td></tr>')
            continue
        d = by_k[k]
        rows.append(f'<tr><td>{k}</td><td><span class="ms">{esc(d["title_ms"])}</span><span class="th">{esc(d["title_th"])}</span></td>'
                    f'<td>{esc(d["clo"])}</td><td><a href="bab/{d["no"]:02d}.html">Bab {d["no"]}</a></td></tr>')
    rows.append('<tr class="ujian"><td>16</td><td><span class="ms"><strong>Peperiksaan Akhir Semester</strong></span>'
                '<span class="th">สอบปลายภาค ครอบคลุมบทที่ 1–14</span></td><td>CLO1</td><td>–</td></tr>')
    jadual = f"""
<section class="bahagian"><h1><span class="ms">Jadual 15 Kelas</span><span class="th">แผนการสอน 15 คาบ</span></h1>
<div class="bi"><p class="ms">Setiap kelas: Khamis 08.00–12.10, bilik 17401 (teori 2 jam, amali 2 jam).</p>
<p class="th">เรียนทุกวันพฤหัสบดี 08.00–12.10 น. ห้อง 17401 · ทุกคาบเริ่มด้วยแบบทดสอบก่อนเรียนและจบด้วยแบบทดสอบหลังเรียน</p></div>
<div class="jadual-bungkus"><table class="jadual-kelas"><thead><tr><th>Kelas<small>คาบ</small></th><th>Tajuk<small>หัวข้อ</small></th><th>CLO</th><th>Pelajaran<small>บทเรียน</small></th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div></section>"""
    (ROOT / "jadual.html").write_text(halaman("jadual.html", "Jadual 15 Kelas", jadual), encoding="utf-8")

    # ---- pelajaran ----
    pel = f"""<section class="bahagian"><h1><span class="ms">Pelajaran</span><span class="th">บทเรียน 14 บท</span></h1>
<div class="bi"><p class="ms">Pilih bab. Setiap bab ada kosa kata, perbualan, latihan dan rumusan.</p><p class="th">เลือกบทที่ต้องการ ทุกบทมีคำศัพท์ บทสนทนา แบบฝึกหัด และสรุปบท</p></div>
<div class="grid-kad">{''.join(kad_bab(d) for d in bab)}</div></section>"""
    (ROOT / "pelajaran.html").write_text(halaman("pelajaran.html", "Pelajaran", pel), encoding="utf-8")

    # ---- bab ----
    for i, d in enumerate(bab):
        secs = [s for s in d["sections"] if not tersembunyi(s)]
        buka = d["no"] in BUKA_JAWAPAN
        isi_secs = "".join(seksyen(s, n + 1, buka) for n, s in enumerate(secs))
        toc = "".join(f'<a href="#s{n + 1}">{esc(re.sub(r"^\d+\.\s*", "", s["ms"]))}</a>' for n, s in enumerate(secs))
        sebelum = bab[i - 1] if i else None
        seterusnya = bab[i + 1] if i + 1 < len(bab) else None
        navb = ""
        if sebelum:
            navb += f'<a href="{sebelum["no"]:02d}.html"><small>‹ Bab {sebelum["no"]}</small><span class="ms">{esc(sebelum["title_ms"])}</span></a>'
        else:
            navb += "<span></span>"
        if seterusnya:
            navb += f'<a class="seterus" href="{seterusnya["no"]:02d}.html"><small>Bab {seterusnya["no"]} ›</small><span class="ms">{esc(seterusnya["title_ms"])}</span></a>'
        isi = f"""
<article class="bab">
<header class="bab-kepala"><p class="kicker">Bab {d['no']} · Kelas {d['kelas']} · {esc(d['clo'])}</p>
<h1><span class="ms">{esc(d['title_ms'])}</span><span class="th">{esc(d['title_th'])}</span></h1>
<div class="alat"><button type="button" id="togol-th" aria-pressed="false">Sembunyikan terjemahan · ซ่อนคำแปล</button>
<a class="alat-pautan" href="../pdf/bab-{d['no']:02d}.pdf" download>Muat turun PDF · ดาวน์โหลด PDF</a>
<button type="button" onclick="window.print()">Cetak · พิมพ์</button></div></header>
<div class="bab-badan"><nav class="toc" aria-label="Kandungan bab"><p>Kandungan · สารบัญ</p>{toc}</nav>
<div class="bab-isi">{isi_secs}</div></div>
<nav class="nav-bab" aria-label="Bab sebelum dan seterusnya">{navb}</nav>
</article>"""
        (ROOT / "bab" / f"{d['no']:02d}.html").write_text(
            halaman(f"bab/{d['no']:02d}.html", f"Bab {d['no']}: {d['title_ms']}", isi, aras="../", aktif="pelajaran.html",
                    keterangan=f"Bab {d['no']}: {d['title_ms']} · {d['title_th']}"), encoding="utf-8")

    # ---- penilaian ----
    bab13 = next(d for d in bab if d["no"] == 13)
    rubrik = next(s for s in bab13["sections"] if "Rubrik Projek" in s["ms"])
    rakan = next(s for s in bab13["sections"] if "Rakan Sekumpulan" in s["ms"])
    bab14 = next(d for d in bab if d["no"] == 14)
    refleksi = next(s for s in bab14["sections"] if "Refleksi" in s["ms"])
    pen = f"""<section class="bahagian"><h1><span class="ms">Penilaian</span><span class="th">การวัดและประเมินผล</span></h1>
<div class="grid-2"><div><h2><span class="ms">Pecahan Markah</span><span class="th">สัดส่วนคะแนน (100%)</span></h2><div class="panel">{bar_markah()}</div></div>
<div><h2><span class="ms">Penilaian sepanjang semester</span><span class="th">การประเมินระหว่างเรียน</span></h2>
<div class="panel"><ul>
<li><span class="ms">Ujian pra dan ujian pasca setiap kelas</span><span class="th">แบบทดสอบก่อนเรียนและหลังเรียนทุกคาบ (ใช้ดูพัฒนาการ ไม่นับคะแนน)</span></li>
<li><span class="ms">Main peranan dan perbualan berpasangan</span><span class="th">บทบาทสมมติและบทสนทนาเป็นคู่ในชั้นเรียน</span></li>
<li><span class="ms">Peperiksaan pertengahan semester (Kelas 8)</span><span class="th">สอบกลางภาค คาบที่ 8 เนื้อหาคาบที่ 1–7</span></li>
<li><span class="ms">Projek kumpulan (Kelas 14–15)</span><span class="th">โครงงานกลุ่ม คาบที่ 14–15</span></li>
<li><span class="ms">Peperiksaan akhir semester</span><span class="th">สอบปลายภาค เนื้อหาบทที่ 1–14</span></li>
</ul></div></div></div></section>
<section class="bahagian">{seksyen(rubrik, 1)}{seksyen(rakan, 2)}{seksyen(refleksi, 3)}</section>"""
    (ROOT / "penilaian.html").write_text(halaman("penilaian.html", "Penilaian", pen), encoding="utf-8")

    # ---- dokumen ----
    baris = "".join(
        f'<tr><td>Bab {d["no"]}</td><td><span class="ms">{esc(d["title_ms"])}</span><span class="th">{esc(d["title_th"])}</span></td>'
        f'<td><a class="muat" href="pdf/bab-{d["no"]:02d}.pdf" download>PDF</a></td>'
        f'<td>{"<span class=\"ms\">Ada</span><span class=\"th\">มีเฉลย</span>" if d["no"] in BUKA_JAWAPAN else "<span class=\"th\">เปิดหลังเรียน</span>"}</td></tr>' for d in bab)
    dok = f"""<section class="bahagian"><h1><span class="ms">Muat Turun</span><span class="th">ดาวน์โหลดเอกสารประกอบการเรียน</span></h1>
<div class="bi"><p class="ms">Dokumen pelajaran untuk setiap bab dalam format PDF. Jawapan latihan dimasukkan selepas bab itu diajar.</p>
<p class="th">เอกสารประกอบการเรียนรายบทเป็นไฟล์ PDF เนื้อหาเหมือนหน้าเว็บ เฉลยแบบฝึกหัดจะอยู่ในไฟล์หลังจากสอนบทนั้นแล้ว ถ้าดาวน์โหลดไว้ก่อนเรียน ให้ดาวน์โหลดใหม่อีกครั้งหลังเรียน</p></div>
<div class="jadual-bungkus"><table><thead><tr><th>Bab</th><th>Tajuk<small>หัวข้อ</small></th><th>Fail<small>ไฟล์</small></th><th>Jawapan<small>เฉลย</small></th></tr></thead><tbody>{baris}</tbody></table></div></section>"""
    (ROOT / "dokumen.html").write_text(halaman("dokumen.html", "Muat Turun", dok), encoding="utf-8")


if __name__ == "__main__":
    bab = muat_bab()
    bina_html(bab)
    print(f"Siap · เสร็จ: {len(bab)} bab")
