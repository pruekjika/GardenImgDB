import "./ImageGallery.css";

const ImageObject = (props: {
  imgUrl: string;
  imgName: string;
  style: string;
  onClick: () => void;
}) => {
  return (
    <div className={`image-container ${props.style}`} onClick={props.onClick}>
      <div className='center-text'>
        <p className='text-img-name'>{`${props.imgName
          .replace("__", "")
          .replace(".webp", "")}`}</p>
        {/* <p className='text-img-date'>{`${props.imgName}`}</p> */}
      </div>
    </div>
  );
};

export default ImageObject;
