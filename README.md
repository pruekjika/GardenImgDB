# GardenImgDB

กระบวนการทำคือ

1. upload ภาพใหญ่ลง database onedrive
2. นำภาพที่ทำให้เล็กลงแล้ว upload ลง github นี้ และ run python file ให้มันทำการสร้างภาพใหม่

the `raw_image` will be store at:
https://kkumail-my.sharepoint.com/:f:/p/nattapongtang/EqQLLNfFRGJFphdrPYlCaF0BiVKuBZ6za8otb0-ZGZnnuA?e=JiDEBm

what will store here will be

- the downscale of `main_image` ~ 2mb for each (original ~ 20mb each)
- the finished `fixed_image` ~ 2mb each

all img is downscale by using `file converter` to .jpg setting with `clamp to lowest power of 2 size`
