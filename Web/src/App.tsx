import "./App.css";
import firstImage from "../../ImageDB/Fixed/__0.jpg";
import secondImage from "../../ImageDB/Fixed/__1.jpg";

function App() {
  return (
    <>
      <div className='container'>
        <h3>Image compare</h3>
        <div className='img-comp-container'>
          <div className='img-comp-img'>
            <img src={firstImage} width='1000' height='700' />
          </div>
          <div className='img-comp-img img-comp-overlay'>
            <img src={secondImage} width='1000' height='700' />
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
