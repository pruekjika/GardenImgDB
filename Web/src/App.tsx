import "./App.css";
import React, { useEffect, useState } from "react";
import CompareZoomPanPinch from "./Components/CompareZoomPanPinch";
import ImageGallery from "./Components/ImageGallery";
import { fetchImagesFromRepo } from "./api";

import { Image } from "./Image";

const owner = "pruekjika";
const repo = "GardenImgDB";

function App() {
  const [images, setImages] = useState<Image[]>([]);

  useEffect(() => {
    fetchImagesFromRepo(owner, repo)
      .then((images) => {
        setImages(images);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }, []);

  return (
    <>
      <ImageGallery images={images} />
      <CompareZoomPanPinch />
    </>
  );
}

export default App;
