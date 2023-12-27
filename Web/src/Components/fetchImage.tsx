const owner = "pruekjika";
const repo = "GardenImgDB";

fetch(`https://api.github.com/repos/${owner}/${repo}/contents`)
  .then((response) => response.json())
  .then((data) => {
    const files = data.filter((item: { type: string }) => item.type === "file");
    const fileNames = files.map((file: { name: unknown }) => file.name);
    console.log(fileNames);
  })
  .catch((error) => {
    console.error("Error:", error);
  });
