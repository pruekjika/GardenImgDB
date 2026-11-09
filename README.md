# GardenImgDB

what will store here will be

- the finished `fixed_image` ~ 2mb each

all img is downscale by using `file converter` to `.jpg/.webp` setting with `clamp to lowest power of 2 size`
so that final size = `4096x3072` = is divide by 2 from original

## website

CompareWeb: [ImageCompare](https://pruekjika.github.io/GardenImgDB/)

## ที่ต้องทำ

1. 2025-06-20 onedrive มหาลัยพังไปแล้วคือ ได้แค่ 5gb ซึ่งไม่พอเก็บภาพ ทำให้ข้ามขั้นตอนนี้ได้ เอาไปไว้ใน google drive นี้แทน https://drive.google.com/drive/folders/1TMBsS2RonKXjFwxCICXABQEelqACY30W?usp=drive_link

2. แก้ภาพให้ตรงกันโดย นำ `__ref` และ `ที่ต้องการจะแก้.jpg` ไปไว้ใน `P-FixingImg-big` (เลือก ref จาก https://kkumail-my.sharepoint.com/:f:/p/nattapongtang/EkM0ZmWS6OlBmL3nbDdIvU0Bh8Rl7Ec9tB7EdT2lznck-Q?e=wYcaJh)
3. run `main.py` เพื่อทำการ fix image ได้ `ImageDB/<เลข>.webp` เลย (ชื่อภาพเป็นเลข เช่น `98.JPG` จะใช้เลขนั้น ถ้าไม่ใช่เลขจะใช้เลขถัดไป)
4. เปิด `__<ชื่อ>_check.jpg` เช็คว่าตรง (ซ้าย = ภาพซ้อน, ขวา = ตารางหมากรุก ถ้าเส้นถนน/ขอบบ่อขาดตอน แปลว่าไม่ตรง) ถ้าไม่ตรง run `python PythonScpt/manual_match.py` แล้วคลิกจุดคู่กัน
5. Upload file `__.jpg` ทีแก้แล้วกลับขึ้นไปใน onedrive

### ทำใหม่ทั้งหมดด้วย ref เดียว (`batch_align.py`)

ใช้ตอนอยากให้ทุกภาพตรงกับ ref ตัวเดียว (แก้ปัญหา error สะสมจากการเปลี่ยน ref หลายรอบ)

1. โหลดภาพ original เต็มขนาดทั้งหมดมาไว้ใน `P-Originals/` ตั้งชื่อตามลำดับ `0.jpg`, `1.jpg`, ... (ลำดับเวลาสำคัญ เพราะภาพจะถูกจับคู่กับภาพข้างเคียง)
2. เลือกภาพ master 1 ภาพ (ฟ้าโปร่ง ไม่มีเงายาว ถ่ายตรงลงมา) แล้ว run
   `python PythonScpt/batch_align.py --src P-Originals --ref 95 --out P-Aligned`
   (ใส่ `--format webp` ถ้าอยากได้ .webp เลย คุณภาพเท่ากับไฟล์ใน ImageDB)
3. เปิด `P-Aligned/report.html` ภาพที่แย่สุดอยู่บนสุด แถวสีแดง = ควรเช็ค
4. ภาพไหนเพี้ยน: `python PythonScpt/manual_match.py --photo P-Originals/40.jpg --ref P-Originals/95.jpg --out P-Aligned` คลิกจุดคู่กัน แล้ว run ข้อ 2 ซ้ำ (รอบหลังเร็ว เพราะมี cache)

### drone setting

บินที่ความสูง 215 m จากพื้นดิน ขึ้นตรงโต๊ะไม้หนัก ด้านข้างศาลาแรกที่พ่อสร้าง

เมื่อก่อนเคยถ่ายวันละ 4 รูปคือ รูปใหญ่ 1 ละ แบ่งย่อยสวนออกเป็น 3 ส่วนละถ่ายอีก แต่หลังๆมา พอไม่ได้ทำนานๆ มันถ่ายแบบเดิมไม่ไหวแล้ว แบบกลับบ้านปีละครั้ง มันลืมการตั้งค่าไปหมด

ดังนั้นเลยลดเหลือถ่าย `ภาพใหญ่เต็มสวน ที่ความสูง 215m` ภาพเดียว เอากลางภาพอยู่ประมาณตรงจุดตัด 3 เหลี่ยม กะๆเอาโลด
