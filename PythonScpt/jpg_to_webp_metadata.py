from PIL import Image

# import webptools
import subprocess
import os


def main():
    jpg_folder_file_path = (
        r"C:\Users\meang\Documents\Github\GardenImgDB\ImageDB\Original"
    )

    webp_folder_file_path = r"C:\Users\meang\Documents\Github\GardenImgDB\ImageDB\Fixed"
    files = os.listdir(jpg_folder_file_path)

    for file_name in files:
        if file_name.endswith(".jpg"):
            jpg_file_path = os.path.join(jpg_folder_file_path, file_name)
            webp_file_path = os.path.join(
                webp_folder_file_path, file_name.replace(".jpg", ".webp")
            )

            # jpg_image = Image.open(jpg_file_path)
            # metadata = jpg_image.info

            # webptools.cwebp(
            #     jpg_file_path,
            #     webp_file_path,
            #     extra_params=["-metadata", f"all={metadata}"],
            # )
            print(jpg_file_path)
            print(webp_file_path)

            subprocess.run(
                ["exiftool", "-TagsFromFile", jpg_file_path, "-all:all", webp_file_path]
            )

            # print(f"do copy {file_name} metadata to {webp_file_path}")


if __name__ == "__main__":
    main()
