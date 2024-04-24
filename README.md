# GardenImgDB

what will store here will be

- the downscale of `main_image` ~ 2mb for each (original ~ 20mb each)
- the finished `fixed_image` ~ 2mb each

all img is downscale by using `file converter` to `.jpg/.webp` setting with `clamp to lowest power of 2 size`
so that final size = `4096x3072` = is divide by 2 from original

### website

CompareWeb: [ImageCompare](https://pruekjika.github.io/GardenImgDB/)

### python

package

- run `pipInstall.bat` once

กระบวนการทำคือ

1. upload `raw_image` ภาพใหญ่ลง database onedrive https://kkumail-my.sharepoint.com/:f:/p/nattapongtang/EqQLLNfFRGJFphdrPYlCaF0B04w2evmpz3C8jPsoT-KX2Q?e=jrJduX

2. นำภาพที่ทำให้เล็กลงแล้ว upload ลง github นี้ และ run python file ให้มันทำการสร้างภาพใหม่
   1. เช็คไฟล์ว่ามีไฟล์ 2 อย่างด้านล่างใน folder `P-FixingImg-big`
      1. ไฟล์ภาพ `__ref` ที่มีอักษร `__` นำหน้า ควรใช้ `__77.jpg` เป็น ref เพราะจะได้เป็นกลาง (เลือก ref จาก https://kkumail-my.sharepoint.com/:f:/p/nattapongtang/EkM0ZmWS6OlBmL3nbDdIvU0Bh8Rl7Ec9tB7EdT2lznck-Q?e=wYcaJh)
      2. ไฟล์ภาพ `ที่ต้องการจะแก้.jpg`
   2. run `main.py` เพื่อทำการ fix image
   3. ถ้าไฟล์ภาพทำได้ไม่มีปัญหา ให้เราทำการ
      1. ใช้ `file converter` convert ออกมา 2 ไฟล์เป็น
         1. downscale.jpg // อันนี้ไม่ใช่อันของ fixed นะ เป็นอัน original.jpg ก่อน fix => `P-Original-resized`
         2. downscale-just-fixed-img.webp => `NowFixedWebp` ปล่อยมันอยู่ด้านนอกเลย ไม่ต้องย้ายเข้า folder
   4. ไปที่ `img_mover.py` ละ run file เพื่อ auto move file

Upload file ทีแก้แล้วกลับขึ้นไปใน onedrive
