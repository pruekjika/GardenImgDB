from exif import Image 

f_path_1 = "./ExampleImg/wa.jpg"
f_path_2 = "./ExampleImg/wa2.jpg"
f_path_3 = "./ExampleImg/wa3.jpg"

with open(f_path_1, "rb") as original_image:
     exif_template = Image(original_image)

if not exif_template.has_exif:
    Warning("No EXIF data found for " + f_path_1)

tags = exif_template.list_all()


with open(f_path_2, "rb") as new_rgb_image:
     exif_new = Image(new_rgb_image)

for tag in tags:
    try:
        exec("exif_new." + tag + "=exif_template." + tag)
    except:
        pass

with open(f_path_3, "wb") as new_rgb_image:
     new_rgb_image.write(exif_new.get_file())