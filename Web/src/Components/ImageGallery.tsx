import React, { useState } from "react";
import "./ImageGallery.css";
import ImageObject from "./ImageObject";
import { Image } from "../Image";

interface ImageGalleryProps {
  images: Image[];
}

const ImageGallery: React.FC<ImageGalleryProps> = ({ images }) => {
  const [selectedImages, setSelectedImages] = useState<Image[]>([]);

  const handleImageClick = (image: Image) => {
    if (selectedImages.length < 2) {
      setSelectedImages((prevSelectedImages) => [...prevSelectedImages, image]);
    } else {
      // If 2 images are already selected, toggle between the first and last selected images
      setSelectedImages((prevSelectedImages) => {
        if (prevSelectedImages[0] === image) {
          return [prevSelectedImages[1]];
        } else {
          return [image, prevSelectedImages[0]];
        }
      });
    }
  };

  const isSelected = (image: Image): boolean => {
    return selectedImages.includes(image);
  };

  return (
    <div className='image-gallery'>
      {images.map((image) => (
        <ImageObject
          key={image.name}
          imgUrl={image.url}
          imgName={image.name}
          onClick={() => handleImageClick(image)}
          style={{
            border: isSelected(image) ? "2px solid blue" : "none",
          }}
        />
      ))}
    </div>
  );
};

export default ImageGallery;
