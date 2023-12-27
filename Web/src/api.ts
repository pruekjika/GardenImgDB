/* eslint-disable @typescript-eslint/no-explicit-any */
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
          item.type === "file" && item.path.match(/\.(jpeg|jpg|png|gif)$/i)
      )
      .map((item: any) => ({
        name: item.name,
        url: item.download_url,
      }));

    return images;
  } catch (error) {
    console.error("Error:", error);
    return [];
  }
}
