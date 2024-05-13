import subprocess
import os

jpg_folder_file_path = r"C:\Users\meang\Documents\Github\GardenImgDB\ImageDB\Original"
webp_folder_file_path = r"C:\Users\meang\Documents\Github\GardenImgDB\ImageDB\Fixed"

files = os.listdir(jpg_folder_file_path)

for file_name in files:
    if file_name.endswith(".jpg"):

        jpg_file_path = os.path.join(jpg_folder_file_path, file_name)
        webp_file_path = os.path.join(
            webp_folder_file_path, file_name.replace(".jpg", ".webp")
        )

        # need to install this first [Installing ExifTool](https://exiftool.org/install.html#Windows)
        subprocess.run(
            ["exiftool", "-TagsFromFile", jpg_file_path, "-all:all", webp_file_path]
        )

        print(f"do copy {file_name} metadata to {webp_file_path}")


def one_line_command():
    data_path = r"C:\Users\meang\Documents\Github\GardenImgDB\ImageDB\Fixed\0.jpg"
    target_path = r"C:\Users\meang\Documents\Github\GardenImgDB\ImageDB\Fixed\__0.webp"
    subprocess.run(["exiftool", "-TagsFromFile", data_path, "-all:all", target_path])
