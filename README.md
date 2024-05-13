# GardenImgDB

what will store here will be

- the finished `fixed_image` ~ 2mb each

all img is downscale by using `file converter` to `.jpg/.webp` setting with `clamp to lowest power of 2 size`
so that final size = `4096x3072` = is divide by 2 from original

### website

CompareWeb: [ImageCompare](https://pruekjika.github.io/GardenImgDB/)

### ที่ต้องทำ

1. upload `raw_image` ภาพใหญ่ลง database onedrive https://kkumail-my.sharepoint.com/:f:/p/nattapongtang/EqQLLNfFRGJFphdrPYlCaF0B2D0Oh5VBAn5-VcLupwrMyw?e=L6f01H
2. แก้ภาพให้ตรงกันโดย นำ `__ref` และ `ที่ต้องการจะแก้.jpg` ไปไว้ใน `P-FixingImg-big` (เลือก ref จาก https://kkumail-my.sharepoint.com/:f:/p/nattapongtang/EkM0ZmWS6OlBmL3nbDdIvU0Bh8Rl7Ec9tB7EdT2lznck-Q?e=wYcaJh)
3. run `main.py` เพื่อทำการ fix image
4. ถ้าไฟล์ภาพทำได้ไม่มีปัญหา ให้เราใช้ file converter แปลงมันให้เป็น .webp
5. ย้าย .webp ไปไว้ใน folder `imageDB`
6. Upload file `__.jpg` ทีแก้แล้วกลับขึ้นไปใน onedrive

### drone setting

บินที่ความสูง 215 m จากพื้นดิน ขึ้นตรงโต๊ะไม้หนัก ด้านข้างศาลาแรกที่พ่อสร้าง

เมื่อก่อนเคยถ่ายวันละ 4 รูปคือ รูปใหญ่ 1 ละ แบ่งย่อยสวนออกเป็น 3 ส่วนละถ่ายอีก แต่หลังๆมา พอไม่ได้ทำนานๆ มันถ่ายแบบเดิมไม่ไหวแล้ว แบบกลับบ้านปีละครั้ง มันลืมการตั้งค่าไปหมด

ดังนั้นเลยลดเหลือถ่าย `ภาพใหญ่เต็มสวน ที่ความสูง 215m` ภาพเดียว เอากลางภาพอยู่ประมาณตรงจุดตัด 3 เหลี่ยม กะๆเอาโลด
