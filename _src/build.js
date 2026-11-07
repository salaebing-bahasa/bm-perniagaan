const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  TableLayoutType, AlignmentType, BorderStyle, ShadingType, Header, Footer, PageNumber,
  LevelFormat, PageBreak,
} = require("docx");

const FONT = "TH SarabunPSK";
const GREEN = "1F5D40", GOLD = "B8860B", GRAY = "4A4A4A", LIGHT = "EEF5F0", GOLDLIGHT = "FAF4E4";
const SIZE = 32; // 16 pt
const W = 9360;  // A4, ขอบ 1 นิ้ว

const isThai = (s) => /[฀-๿]/.test(s);
// แยกข้อความไทย/ละตินเป็น TextRun คนละตัว
function runs(text, o = {}) {
  const parts = text.match(/([฀-๿]+(?:[\s฀-๿]*[฀-๿])?|[^฀-๿]+)/g) || [text];
  return parts.map((p) => new TextRun({
    text: p, font: FONT, size: o.size || SIZE, bold: o.bold, italics: o.italics,
    color: o.color || (isThai(p) && o.thaiGray ? GRAY : o.color),
    language: isThai(p) ? { value: "th-TH" } : { value: "ms-MY" },
  }));
}
// ข้อความผสมตัวหนา: **...**
function rich(text, o = {}) {
  const out = [];
  text.split(/(\*\*[^*]+\*\*)/).forEach((seg) => {
    if (!seg) return;
    const b = seg.startsWith("**");
    out.push(...runs(b ? seg.slice(2, -2) : seg, { ...o, bold: b || o.bold }));
  });
  return out;
}
const P = (text, o = {}) => new Paragraph({
  children: rich(text, o), alignment: o.align || AlignmentType.LEFT,
  spacing: { after: o.after ?? 80, before: o.before ?? 0, line: 300 },
  indent: o.indent ? { left: o.indent } : undefined,
});
// มลายูบน ไทยล่าง
const BI = (ms, th, o = {}) => [P(ms, { ...o, after: 20 }), P(th, { ...o, color: GRAY, after: o.after ?? 140 })];
const H1 = (ms, th) => [
  new Paragraph({ children: runs(ms, { size: 40, bold: true, color: GREEN }), spacing: { before: 240, after: 0 }, keepNext: true, keepLines: true,
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: GOLD, space: 4 } } }),
  new Paragraph({ children: runs(th, { size: 32, bold: true, color: GOLD }), spacing: { before: 60, after: 160 }, keepNext: true }),
];
const H2 = (ms, th) => new Paragraph({
  children: [...runs(ms, { size: 34, bold: true, color: GREEN }), ...runs("  " + th, { size: 30, bold: true, color: GOLD })],
  spacing: { before: 200, after: 100 }, keepNext: true,
});
const bullet = (text, o = {}) => new Paragraph({ children: rich(text, o), numbering: { reference: "dot", level: 0 }, spacing: { after: 40, line: 300 } });
const biBullet = (ms, th) => [
  new Paragraph({ children: rich(ms), numbering: { reference: "dot", level: 0 }, spacing: { after: 0, line: 300 } }),
  new Paragraph({ children: rich(th, { color: GRAY }), indent: { left: 720 }, spacing: { after: 80, line: 300 } }),
];

const border = { style: BorderStyle.SINGLE, size: 4, color: "B9C9BF" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(widths, header, rows, o = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (content, w, head, shade) => new TableCell({
    width: { size: w, type: WidthType.DXA }, borders,
    shading: head ? { type: ShadingType.CLEAR, fill: GREEN, color: "auto" } : shade ? { type: ShadingType.CLEAR, fill: shade, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: (Array.isArray(content) ? content : [content]).map((t, i) => new Paragraph({
      children: rich(String(t), { color: head ? "FFFFFF" : ((Array.isArray(content) && content.length === 3 ? i === 2 : i > 0) ? GRAY : undefined), bold: head, size: o.size || 30 }),
      spacing: { after: 0, line: 280 }, alignment: o.center && o.center.includes(widths.indexOf(w)) ? AlignmentType.CENTER : AlignmentType.LEFT,
    })),
  });
  const trs = [];
  if (header) trs.push(new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, widths[i], true)) }));
  rows.forEach((r, ri) => trs.push(new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, widths[i], false, ri % 2 ? LIGHT : undefined)) })));
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED, rows: trs });
}
function box(lines, fill = GOLDLIGHT) {
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: [W], layout: TableLayoutType.FIXED,
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({
      width: { size: W, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill, color: "auto" },
      borders: { top: { style: BorderStyle.SINGLE, size: 4, color: GOLD }, bottom: { style: BorderStyle.SINGLE, size: 4, color: GOLD }, left: { style: BorderStyle.SINGLE, size: 24, color: GOLD }, right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" } },
      margins: { top: 100, bottom: 100, left: 180, right: 180 },
      children: lines,
    })] })],
  });
}
const sp = (n = 120) => new Paragraph({ children: [], spacing: { after: n } });

const C = JSON.parse(fs.readFileSync(process.argv[3] || "content.json", "utf8"));
const CH = C.chapter || 1;
const body = [];
const add = (...x) => x.flat().forEach((e) => body.push(e));

// ---------- หัวบท ----------
add(new Paragraph({ children: runs("1503250 Bahasa Melayu untuk Perniagaan · ภาษามลายูเพื่อธุรกิจ", { size: 28, color: GOLD, bold: true }), alignment: AlignmentType.CENTER, spacing: { after: 60 } }));
add(new Paragraph({ children: runs(`BAB ${CH}  ·  บทที่ ${CH}`, { size: 30, color: GREEN, bold: true }), alignment: AlignmentType.CENTER, spacing: { after: 40 } }));
add(new Paragraph({ children: runs(C.title_ms, { size: 48, bold: true, color: GREEN }), alignment: AlignmentType.CENTER, spacing: { after: 20 } }));
add(new Paragraph({ children: runs(C.title_th, { size: 38, bold: true, color: GREEN }), alignment: AlignmentType.CENTER, spacing: { after: 160 } }));
add(table([2200, 7160], null, C.meta, { size: 30 }));
add(sp(160));

for (const sec of C.sections) {
  add(H1(sec.ms, sec.th));
  for (const b of sec.blocks) {
    if (b.t === "bi") add(BI(b.ms, b.th));
    else if (b.t === "h2") add(H2(b.ms, b.th));
    else if (b.t === "bullets") b.items.forEach((it) => add(Array.isArray(it) ? biBullet(it[0], it[1]) : bullet(it)));
    else if (b.t === "table") { add(table(b.w, b.head, b.rows, { size: b.size })); if (b.after !== -1) add(sp(b.after ?? 160)); }
    else if (b.t === "box") { add(box(b.lines.map((l) => P(l[0], { color: l[1] ? GRAY : undefined, after: l[2] ?? 40, bold: l[3] })))); add(sp(160)); }
    else if (b.t === "p") add(P(b.text, { color: b.gray ? GRAY : undefined, after: b.after, bold: b.bold }));
    else if (b.t === "dialog") {
      const rows = b.lines.map(([who, ms, th]) => [`**${who}**`, [ms, th]]);
      add(table([1500, 7860], null, rows, { size: 30 })); add(sp(160));
    }
    else if (b.t === "pagebreak") add(new Paragraph({ children: [new PageBreak()] }));
  }
}

const doc = new Document({
  creator: "ผศ.มูหำหมัด สาแลบิง",
  title: `1503250 บทที่ ${CH}`,
  styles: { default: { document: { run: { font: FONT, size: SIZE } } } },
  numbering: { config: [{ reference: "dot", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1300, left: 1273, right: 1273 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: runs(`1503250 ภาษามลายูเพื่อธุรกิจ · บทที่ ${CH}`, { size: 24, color: GOLD }) })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 26, color: GREEN })] })] }) },
    children: body,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(process.argv[2] || "out.docx", b); console.log("ok"); });
