import {
  ReactCompareSlider,
  ReactCompareSliderImage,
  ReactCompareSliderHandle,
} from "react-compare-slider";

const CompareImageSlider = (props: { img1: string; img2: string }) => {
  return (
    <div>
      <ReactCompareSlider
        onlyHandleDraggable={true}
        boundsPadding={0}
        itemOne={<ReactCompareSliderImage alt='Image one' src={props.img1} />}
        itemTwo={<ReactCompareSliderImage alt='Image two' src={props.img2} />}
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
