# GardenImgDB

กระบวนการทำคือ

1. upload `raw_image` ภาพใหญ่ลง database onedrive https://kkumail-my.sharepoint.com/:f:/p/nattapongtang/EqQLLNfFRGJFphdrPYlCaF0BiVKuBZ6za8otb0-ZGZnnuA?e=JiDEBm
2. นำภาพที่ทำให้เล็กลงแล้ว upload ลง github นี้ และ run python file ให้มันทำการสร้างภาพใหม่

what will store here will be

- the downscale of `main_image` ~ 2mb for each (original ~ 20mb each)
- the finished `fixed_image` ~ 2mb each

all img is downscale by using `file converter` to .jpg setting with `clamp to lowest power of 2 size`

// new system use to `.webp` with `clamp to lowest power of 2 size` so that final size = `4096x3072` = divide by 2 from original
