import React from "react";
import CompareImageSlider from "./CompareImageSlider.js";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import "./ImageGallery.css";

const CompareZoomPanPinch = (props: { img1: string; img2: string }) => {
  return (
    <div className='container'>
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
            <TransformComponent>
              {<CompareImageSlider img1={props.img1} img2={props.img2} />}
            </TransformComponent>
          </React.Fragment>
        )}
      </TransformWrapper>
    </div>
  );
};

export default CompareZoomPanPinch;
