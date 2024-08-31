import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/axios';

function SnowAI() { 
  const { user } = useAuth();
  const [textInput, setTextInput] = useState('');
  const [imageInput, setImageInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('dall-e-3');
  const [textOutput, setTextOutput] = useState('');
  const [imageOutput, setImageOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await api.post('/api/ai/text', { prompt: textInput });
      setTextOutput(response.data.response);
    } catch (error) {
      console.error('Error:', error);
      setTextOutput('An error occurred while processing your text request.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setImageOutput('');
    try {
      const response = await api.post('/api/ai/image', { 
        prompt: imageInput,
        model: selectedModel
      });
      if (response.data.image_url) {
        setImageOutput(response.data.image_url);
      } else {
        throw new Error('No image URL received');
      }
    } catch (error) {
      console.error('Error:', error);
      setImageOutput('An error occurred while processing your image request.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return <p>Please log in to use the AI assistant.</p>;
  }

  return (
    <div className="ai-page">
      <h2>Snow-AI Assistant</h2>
      <div className="ai-section">
        <h3>Text Generation</h3>
        <form onSubmit={handleTextSubmit}>
          <textarea
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Enter your text prompt here"
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Processing...' : 'Generate Text'}
          </button>
        </form>
        {textOutput && (
          <div className="ai-output">
            <h4>Generated Text:</h4>
            <p>{textOutput}</p>
          </div>
        )}
      </div>
      <div className="ai-section">
        <h3>Image Generation</h3>
        <form onSubmit={handleImageSubmit}>
          <textarea
            value={imageInput}
            onChange={(e) => setImageInput(e.target.value)}
            placeholder="Enter your image prompt here"
          />
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            <option value="flux-dev">Flux Dev</option>
            <option value="fal-flux-schnell">Flux Schnell</option>
            <option value="fal-sd-v3-medium">Stable Diffusion v3</option>
            <option value="fal-flux-realism">Flux Realism</option>
            <option value="fal-ai/flux-lora">Flux LoRA</option>
          </select>
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Processing...' : 'Generate Image'}
          </button>
        </form>
        {imageOutput && (
          <div className="ai-output">
            <h4>Generated Image:</h4>
            {typeof imageOutput === 'string' && imageOutput.startsWith('http') ? (
              <img src={imageOutput} alt="AI Generated" className="ai-image" />
            ) : (
              <p>{imageOutput}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default SnowAI;