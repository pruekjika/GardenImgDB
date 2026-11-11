# GardenImgDB

what will store here will be

- the finished `fixed_image` ~ 2mb each

all img is downscale by using `file converter` to `.jpg/.webp` setting with `clamp to lowest power of 2 size`
so that final size = `4096x3072` = is divide by 2 from original

## website

CompareWeb: [ImageCompare](https://pruekjika.github.io/WebImageCompare/)

The site reads the photo list and dates from `ImageDB/index.json`, not the GitHub API.
Rebuild it by hand with `python PythonScpt/Util/image_index.py ImageDB`.

## เพิ่มภาพใหม่ 1 ภาพ (ทำทุกครั้งที่ถ่ายภาพใหม่)

ภาพ original เต็มขนาดเก็บใน google drive (2025-06-20 onedrive มหาลัยเหลือแค่ 5gb ไม่พอ): <https://drive.google.com/drive/folders/1TMBsS2RonKXjFwxCICXABQEelqACY30W?usp=drive_link>

1. ไม่ต้องวาง ref แล้ว: `main.py` ใช้ภาพล่าสุดใน `ImageDB` เป็น ref เอง (ทุกภาพใน ImageDB จัดตรงกับ master 61 แล้ว และภาพล่าสุดฤดูใกล้กันที่สุด จับคู่ได้แม่นกว่า)
   - อยากล็อก ref เป็นภาพเดียว: ตั้ง `REFERENCE_NUMBER` ใน `PythonScpt/Util/folder_util.py` (เช่น `61`)
   - อยากใช้ ref อื่นแค่ครั้งเดียว: วางไฟล์ชื่อขึ้นต้นด้วย `__` ใน `P-FixingImg-big/`
   - ย้ายภาพเก่าที่ทำเสร็จแล้วออกก่อน (เช่น `97.JPG`) ไม่งั้น `main.py` จะหยิบภาพเก่าแล้วหยุด เพราะ `ImageDB/97.webp` มีแล้ว
2. วางภาพใหม่ใน `P-FixingImg-big/` ตั้งชื่อเป็นเลขถัดไป เช่น `98.JPG` (ถ้าไม่ใช่เลข จะได้เลขถัดไปให้เอง และเปลี่ยนชื่อไฟล์เป็นเลขนั้น)
3. ดับเบิลคลิก `run_main.bat` (หรือ `python PythonScpt/main.py` จากโฟลเดอร์ repo)
   ได้ `ImageDB/98.webp` (มีวันที่/GPS จากภาพเดิม) และ `ImageDB/index.json` อัปเดตให้ ถ้า error ดูใน `meangpu.log`
4. เปิด `__98_check.jpg` ที่โฟลเดอร์ repo เช็คว่าตรง (ซ้าย = ภาพซ้อน, ขวา = ตารางหมากรุก ถ้าเส้นถนน/ขอบบ่อขาดตอน แปลว่าไม่ตรง)
   ถ้าไม่ตรง run `python PythonScpt/manual_match.py` แล้วคลิกจุดคู่กัน
5. commit `ImageDB/98.webp` คู่กับ `ImageDB/index.json` เสมอ แล้ว push เว็บจะเห็นภาพใหม่ภายใน ~5 นาที
6. เอาภาพ original ไปเก็บใน google drive ด้านบน แล้วย้ายออกจาก `P-FixingImg-big/`

### ทำใหม่ทั้งหมดด้วย ref เดียว (`batch_align.py`)

ใช้ตอนอยากให้ทุกภาพตรงกับ ref ตัวเดียว (แก้ปัญหา error สะสมจากการเปลี่ยน ref หลายรอบ)

1. โหลดภาพ original เต็มขนาดทั้งหมดจาก google drive มาไว้ใน `P-Originals/` ตั้งชื่อตามเลขใน `ImageDB` (`0.jpg`, `1.jpg`, ...) จับคู่ด้วยวันที่ EXIF กับ `ImageDB/index.json` เพราะชื่อไฟล์ใน drive ไม่ตรงเลขทุกภาพ (ลำดับเวลาสำคัญ เพราะภาพจะถูกจับคู่กับภาพข้างเคียง)
   - ภาพ 9, 87-90 ไม่มี original ใช้ `ImageDB/<เลข>.webp` แทน
2. master ปัจจุบันคือภาพ 61 (2022-12-25 15:01 เงาสั้นสุด) แล้ว run
   `python PythonScpt/batch_align.py --src P-Originals --ref 61 --out P-Aligned`
   (ใส่ `--format webp` ถ้าอยากได้ .webp เลย คุณภาพเท่ากับไฟล์ใน ImageDB; ได้ `index.json` ใน `--out` ด้วย ก๊อปไปพร้อมภาพ)
3. เปิด `P-Aligned/report.html` ภาพที่แย่สุดอยู่บนสุด แถวสีแดง = ควรเช็ค
4. ภาพไหนเพี้ยน: `python PythonScpt/manual_match.py --photo P-Originals/40.jpg --ref P-Originals/61.jpg --out P-Aligned` คลิกจุดคู่กัน แล้ว run ข้อ 2 ซ้ำ (รอบหลังเร็ว เพราะมี cache)

### drone setting

บินที่ความสูง 215 m จากพื้นดิน ขึ้นตรงโต๊ะไม้หนัก ด้านข้างศาลาแรกที่พ่อสร้าง

เมื่อก่อนเคยถ่ายวันละ 4 รูปคือ รูปใหญ่ 1 ละ แบ่งย่อยสวนออกเป็น 3 ส่วนละถ่ายอีก แต่หลังๆมา พอไม่ได้ทำนานๆ มันถ่ายแบบเดิมไม่ไหวแล้ว แบบกลับบ้านปีละครั้ง มันลืมการตั้งค่าไปหมด

ดังนั้นเลยลดเหลือถ่าย `ภาพใหญ่เต็มสวน ที่ความสูง 215m` ภาพเดียว เอากลางภาพอยู่ประมาณตรงจุดตัด 3 เหลี่ยม กะๆเอาโลด
