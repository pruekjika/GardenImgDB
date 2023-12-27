/* eslint-disable @typescript-eslint/no-explicit-any */

// `https://api.github.com/repos/pruekjika/GardenImgDB/contents/ImageDB/Fixed/`
import { Image } from "./Image";

export async function fetchImagesFromRepo(
  owner: string,
  repo: string
): Promise<Image[]> {
  try {
    const response = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/contents/ImageDB/Fixed/`
    );
    if (!response.ok) {
      throw new Error("Failed to fetch repository contents");
    }
    const data = await response.json();

    const images: Image[] = data
      .filter(
        (item: any) =>
          item.type === "file" && item.path.match(/\.(jpeg|jpg|png|gif|webp)$/i)
      )
      .map((item: any) => ({
        name: item.name,
        url: item.download_url,
      }))
      .sort((a: Image, b: Image) => {
        const regex = /\d+/g;
        const aNumber = Number(a.name.match(regex)?.[0]);
        const bNumber = Number(b.name.match(regex)?.[0]);
        return aNumber - bNumber;
      });

    return images;
  } catch (error) {
    console.error("Error:", error);
    return [];
  }
}
