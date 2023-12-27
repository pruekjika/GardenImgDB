import "./ImageGallery.css";

const ImageObject = (props: { image: string; index: number }) => {
  return (
    <div className='image-container'>
      <img src={props.image} alt={`Image ${props.index}`} />
      <div className='center'>
        <h3>{`${props.index + 1}`}</h3>
        <p>{`${props.index}`}</p>
      </div>
    </div>
  );
};

export default ImageObject;
