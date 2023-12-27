import "./App.css";
import firstImage from "../../ImageDB/Fixed/__1.jpg";
import secondImage from "../../ImageDB/Fixed/__19.jpg";

import {
  ReactCompareSlider,
  ReactCompareSliderImage,
} from "react-compare-slider";

function App() {
  return (
    <>
      <div className='container'>
        <div>
          <ReactCompareSlider
            boundsPadding={0}
            itemOne={
              <ReactCompareSliderImage alt='Image one' src={firstImage} />
            }
            itemTwo={
              <ReactCompareSliderImage alt='Image two' src={secondImage} />
            }
            keyboardIncrement='5%'
            position={50}
            style={{
              height: "100vh",
              width: "100%",
            }}
          />
        </div>
      </div>
    </>
  );
}

export default App;
