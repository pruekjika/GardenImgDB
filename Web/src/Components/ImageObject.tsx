import "./ImageGallery.css";

const ImageObject = (props: {
  imgUrl: string;
  imgName: string;
  style: React.CSSProperties;
  onClick: () => void;
}) => {
  return (
    <div
      className='image-container'
      onClick={props.onClick}
      style={props.style}
    >
      <img
        src={props.imgUrl}
        loading='lazy'
        decoding='async'
        alt={`Image ${props.imgName}`}
        sizes='(max-width: 100px) 90px, 73px'
      />
      <div className='center-text'>
        <p className='text-img-name'>{`${props.imgName
          .replace("__", "")
          .replace(".webp", "")}`}</p>
        <p className='text-img-date'>{`${props.imgName}`}</p>
      </div>
    </div>
  );
};

export default ImageObject;
