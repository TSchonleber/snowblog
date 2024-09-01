import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/axios';
import ImageUploader from './ImageUploader';
import './AIPage.css';

function SnowDump() { 
  const { user } = useAuth();
  const [imageInput, setImageInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('flux-dev');
  const [imageOutput, setImageOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedImages, setUploadedImages] = useState([]);
  const [error, setError] = useState('');

  const handleImageSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setImageOutput('');
    setError('');
    
    const formData = new FormData();
    if (imageInput.trim()) {
      formData.append('prompt', imageInput);
    }
    formData.append('model', selectedModel);
    uploadedImages.forEach((image, index) => {
      formData.append(`image${index}`, image);
    });

    try {
      if (!imageInput.trim() && uploadedImages.length === 0) {
        throw new Error('Please provide a prompt or upload an image');
      }
      const response = await api.post('/api/ai/image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      if (response.data.image_data) {
        setImageOutput(response.data.image_data);
      } else {
        throw new Error('No image data received');
      }
    } catch (error) {
      console.error('Error:', error);
      setError(error.message || 'An error occurred while processing your image request.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleImagesSelected = (images) => {
    setUploadedImages(images);
  };

  if (!user) {
    return <p>Please log in to use the Snow-Dump feature.</p>;
  }

  return (
    <div className="snow-dump" style={{ width: '100%' }}>
      <h2 className="glitch" data-text="Snow-Dump">Snow-Dump</h2>
      <div className="snow-dump-container">
        <div className="input-panel">
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="model-select neon-border"
          >
            <option value="flux-dev">Flux Dev</option>
            <option value="fal-flux-schnell">Flux Schnell</option>
            <option value="fal-sd-v3-medium">Stable Diffusion v3</option>
            <option value="fal-flux-realism">Flux Realism</option>
            <option value="fal-ai/flux-lora">Flux LoRA</option>
            <option value="fal-ai/flux/dev/image-to-image">Image to Image</option>
          </select>
          <ImageUploader onImagesSelected={handleImagesSelected} />
          <textarea
            value={imageInput}
            onChange={(e) => setImageInput(e.target.value)}
            placeholder="Describe the image you want to generate..."
            className="prompt-input neon-border"
          />
          <button onClick={handleImageSubmit} disabled={isLoading} className="generate-button neon-border">
            {isLoading ? 'Generating...' : 'Generate Image'}
          </button>
        </div>
        <div className="output-panel">
          {isLoading && <div className="loading">Generating image...</div>}
          {error && <div className="error">{error}</div>}
          {imageOutput && (
            <img src={imageOutput} alt="AI Generated" className="generated-image neon-border" />
          )}
        </div>
      </div>
    </div>
  );
}

export default SnowDump;