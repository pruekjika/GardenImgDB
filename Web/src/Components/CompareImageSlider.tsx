import {
  ReactCompareSlider,
  ReactCompareSliderImage,
  ReactCompareSliderHandle,
} from "react-compare-slider";

const Img1 =
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__2.jpg";
const Img2 =
  "https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__71.jpg";

const CompareImageSlider = () => {
  return (
    <div>
      <ReactCompareSlider
        onlyHandleDraggable={true}
        boundsPadding={0}
        itemOne={<ReactCompareSliderImage alt='Image one' src={Img1} />}
        itemTwo={<ReactCompareSliderImage alt='Image two' src={Img2} />}
        handle={
          <ReactCompareSliderHandle
            buttonStyle={{
              border: 0,
              backdropFilter: "none",
              WebkitBackdropFilter: "none",
              boxShadow: "none",
            }}
            linesStyle={{
              opacity: 0,
            }}
          />
        }
        keyboardIncrement='5%'
        position={50}
        style={{
          height: "100vh",
          width: "100vw",
        }}
      />
    </div>
  );
};

export default CompareImageSlider;
