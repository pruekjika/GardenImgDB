import React from "react";
import CompareImageSlider from "./CompareImageSlider.js";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

const CompareZoomPanPinch = () => {
  return (
    <TransformWrapper
      initialScale={1}
      initialPositionX={200}
      initialPositionY={100}
      maxScale={20}
      centerZoomedOut={true}
      centerOnInit={true}
      disablePadding={true}
      smooth={false}
    >
      {({ zoomIn, zoomOut, resetTransform }) => (
        <React.Fragment>
          <div className='tools'>
            <button onClick={() => zoomIn()}>zoomIn +</button>
            <button onClick={() => zoomOut()}>zoomOut -</button>
            <button onClick={() => resetTransform()}>Reset</button>
          </div>
          <TransformComponent>{<CompareImageSlider />}</TransformComponent>
        </React.Fragment>
      )}
    </TransformWrapper>
  );
};

export default CompareZoomPanPinch;
