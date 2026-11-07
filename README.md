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
| `dokumen.html`, `dokumen/*.docx` | Dokumen versi pelajar | เอกสารฉบับนิสิต |

## Mengemas kini · วิธีแก้ไขเนื้อหา

เนื้อหาบทเรียนทั้งหมดอยู่ใน `_src/bab/bab01.json` – `bab14.json` (ไฟล์เดียวกับที่ใช้สร้างเอกสารประกอบการสอน)
หลังแก้ไขให้สร้างหน้าเว็บใหม่ด้วยคำสั่ง

```
python3 _src/build.py          # สร้างหน้าเว็บ
python3 _src/build.py --docx   # สร้างหน้าเว็บ + ไฟล์ .docx ฉบับนิสิต (ต้องมี node และแพ็กเกจ docx)
```

ส่วนสำหรับผู้สอน (Ujian Pra/Pasca, Skrip Guru, Aktiviti Pembelajaran) ไม่แสดงบนเว็บและไม่อยู่ในไฟล์ฉบับนิสิต
ส่วนเฉลยแบบฝึกหัดซ่อนไว้ในปุ่ม "ดูเฉลย"

สถิติผู้เข้าชม: GoatCounter รหัส `bm-perniagaan`
