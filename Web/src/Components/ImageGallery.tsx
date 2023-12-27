import React from "react";
import "./ImageGallery.css";
import ImageObject from "./ImageObject";
import { Image } from "../Image";

interface ImageGallery {
  images: Image[];
}

const ImageGallery: React.FC<ImageGallery> = ({ images }) => {
  return (
    <div className='image-gallery'>
      {images.map((image, index) => (
        <ImageObject key={image.name} image={image.url} index={index} />
      ))}
    </div>
  );
};

export default ImageGallery;
