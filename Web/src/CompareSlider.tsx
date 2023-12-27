import {
  ReactCompareSlider,
  ReactCompareSliderImage,
} from "react-compare-slider";

const CompareSlider = () => {
  return (
    <div>
      <ReactCompareSlider
        onlyHandleDraggable={true}
        boundsPadding={0}
        itemOne={
          <ReactCompareSliderImage
            alt='Image one'
            src='https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__2.jpg'
          />
        }
        itemTwo={
          <ReactCompareSliderImage
            alt='Image two'
            src='https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__71.jpg'
          />
        }
        keyboardIncrement='5%'
        position={50}
        style={{
          height: "100vh",
          width: "100%",
        }}
      />
    </div>
  );
};

export default CompareSlider;
