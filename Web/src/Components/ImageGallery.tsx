import React from "react";
import "./ImageGallery.css";
import ImageObject from "./ImageObject";

interface ImageGallery {
  images: string[];
}

const ImageGallery: React.FC<ImageGallery> = ({ images }) => {
  return (
    <div className='image-gallery'>
      {images.map((image, index) => (
        <ImageObject image={image} index={index} />
      ))}
    </div>
  );
};

export default ImageGallery;
