import "./App.css";
// import firstImage from "../../ImageDB/Fixed/__1.jpg";
// import secondImage from "../../ImageDB/Fixed/__19.jpg";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import {
  ReactCompareSlider,
  ReactCompareSliderImage,
} from "react-compare-slider";

function App() {
  return (
    <>
      <div className='container'>
        <TransformWrapper>
          <TransformComponent>
            <ReactCompareSlider
              onlyHandleDraggable={true}
              boundsPadding={0}
              itemOne={
                <ReactCompareSliderImage
                  alt='Image one'
                  src='https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__1.jpg'
                />
              }
              itemTwo={
                <ReactCompareSliderImage
                  alt='Image two'
                  src='https://raw.githubusercontent.com/pruekjika/GardenImgDB/main/ImageDB/Fixed/__70.jpg'
                />
              }
              keyboardIncrement='5%'
              position={50}
              style={{
                height: "100vh",
                width: "100%",
              }}
            />
          </TransformComponent>
        </TransformWrapper>
      </div>
    </>
  );
}

export default App;
