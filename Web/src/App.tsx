import "./App.css";
import React from "react";
import CompareSlider from "./CompareSlider.jsx";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

function App() {
  return (
    <>
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
              <TransformComponent>{<CompareSlider />}</TransformComponent>
            </React.Fragment>
          )}
        </TransformWrapper>
      </div>
    </>
  );
}

export default App;
