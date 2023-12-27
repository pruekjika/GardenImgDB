import React from "react";
import CompareImageSlider from "./CompareImageSlider.js";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import "./ImageGallery.css";

const CompareZoomPanPinch = (props: { img1: string; img2: string }) => {
  return (
    <div className='full-container'>
      <div className='container'>
        <TransformWrapper
          initialScale={0.58}
          maxScale={20}
          minScale={0.58}
          centerOnInit={true}
          disablePadding={true}
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
    </div>
  );
};

export default CompareZoomPanPinch;
