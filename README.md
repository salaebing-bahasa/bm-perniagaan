# 1503250 Bahasa Melayu untuk Perniagaan · ภาษามลายูเพื่อธุรกิจ

Laman kursus untuk pelajar tahun 2, Pengurusan Logistik, Universiti Thaksin (semester 2/2569).
เว็บไซต์รายวิชาสำหรับนิสิตชั้นปีที่ 2 วิชาเอกการจัดการโลจิสติกส์ มหาวิทยาลัยทักษิณ

Pensyarah · ผู้สอน: ผศ.มูหำหมัด สาแลบิง

## Halaman · หน้าเว็บ

| Fail | Kandungan | เนื้อหา |
|---|---|---|
| `index.html` | Laman utama, maklumat kelas, CLO, pecahan markah | หน้าแรก ข้อมูลการเรียน CLOs สัดส่วนคะแนน |
| `jadual.html` | Jadual 15 kelas | แผนการสอน 15 คาบ |
| `pelajaran.html`, `bab/01.html`–`bab/14.html` | 14 bab pelajaran | บทเรียน 14 บท |
| `penilaian.html` | Pecahan markah, rubrik projek, penilaian rakan, refleksi | การวัดผลและ Rubric |
| `dokumen.html`, `pdf/bab-NN.pdf` | PDF setiap bab | ไฟล์ PDF รายบท (เนื้อหาเหมือนหน้าเว็บ) |

## Mengemas kini · วิธีแก้ไขเนื้อหา

เนื้อหาบทเรียนทั้งหมดอยู่ใน `_src/bab/bab01.json` – `bab14.json` (ไฟล์เดียวกับที่ใช้สร้างเอกสารประกอบการสอน)
หลังแก้ไขให้สร้างหน้าเว็บใหม่ด้วยคำสั่ง

```
python3 _src/build.py   # สร้างหน้าเว็บ
python3 _src/pdf.py     # สร้าง PDF รายบทจากหน้าเว็บ (ต้องมี playwright)
```

**เปิดเฉลยหลังสอน:** ใน `_src/build.py` เพิ่มเลขบทในบรรทัด `BUKA_JAWAPAN = []` เช่น `BUKA_JAWAPAN = [1, 2]`
แล้วสร้างหน้าเว็บและ PDF ใหม่ บทที่ยังไม่เปิดจะแสดงข้อความ "เฉลยจะเปิดหลังเรียนคาบนี้" ทั้งบนเว็บและใน PDF

ส่วนสำหรับผู้สอน (Ujian Pra/Pasca, Skrip Guru, Aktiviti Pembelajaran) ไม่แสดงบนเว็บและไม่อยู่ใน PDF

สถิติผู้เข้าชม: GoatCounter รหัส `bm-perniagaan`
