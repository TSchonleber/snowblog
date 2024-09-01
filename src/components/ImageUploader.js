import React, { useState } from 'react';
import './ImageUploader.css';

function ImageUploader({ onImagesSelected }) {
  const [selectedImages, setSelectedImages] = useState([]);

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    const newImages = files.map(file => ({
      file,
      preview: URL.createObjectURL(file)
    }));
    setSelectedImages(prev => [...prev, ...newImages]);
    onImagesSelected([...selectedImages, ...newImages].map(img => img.file));
  };

  const removeImage = (index) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index));
    onImagesSelected(selectedImages.filter((_, i) => i !== index).map(img => img.file));
  };

  return (
    <div className="image-uploader">
      <input
        type="file"
        onChange={handleImageUpload}
        accept="image/*"
        multiple
        id="image-upload"
        className="image-upload-input"
      />
      <label htmlFor="image-upload" className="image-upload-label">
        Choose Images
      </label>
      <div className="image-grid">
        {selectedImages.map((image, index) => (
          <div key={index} className="image-item">
            <img src={image.preview} alt={`Upload ${index}`} />
            <button onClick={() => removeImage(index)} className="remove-image">×</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ImageUploader;