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
      <img src={props.imgUrl} alt={`Image ${props.imgName}`} />
      <div className='center'>
        <p className='image-index'>{`${props.imgName
          .replace("__", "")
          .replace(".jpg", "")}`}</p>
        <p className='date'>{`${props.imgName}`}</p>
      </div>
    </div>
  );
};

export default ImageObject;
