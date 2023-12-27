import "./ImageGallery.css";

const ImageObject = (props: { image: string; index: number }) => {
  return (
    <div className='image-container'>
      <img src={props.image} alt={`Image ${props.index}`} />
      <div className='center'>
        <p className='image-index'>{`${props.index + 1}`}</p>
        <p className='date'>{`${props.index}`}</p>
      </div>
    </div>
  );
};

export default ImageObject;
