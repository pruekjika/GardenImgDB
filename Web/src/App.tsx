import "./App.css";
import CompareZoomPanPinch from "./Components/CompareZoomPanPinch";
import ImageGallery from "./Components/ImageGallery";

const images = [
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__1.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__2.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__3.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__4.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__5.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__6.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__7.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__8.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__9.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__10.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__11.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__12.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__13.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__14.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__15.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__16.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__17.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__18.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__19.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__20.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__21.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__22.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__23.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__24.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__25.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__26.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__27.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__28.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__29.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__30.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__31.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__32.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__33.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__34.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__35.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__36.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__37.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__38.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__39.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__40.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__41.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__42.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__43.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__44.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__45.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__46.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__47.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__48.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__49.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__50.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__51.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__52.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__53.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__54.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__55.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__56.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__57.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__58.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__59.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__60.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__61.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__62.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__63.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__64.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__65.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__66.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__67.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__68.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__69.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__70.jpg",
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__71.jpg",
];

function App() {
  return (
    <>
      <ImageGallery images={images} />
      <CompareZoomPanPinch />
    </>
  );
}

export default App;
