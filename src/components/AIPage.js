import React, { useState } from 'react';
import axios from 'axios';
import './AIPage.css';

function AIPage() {
  const [prompt, setPrompt] = useState('');
  const [generatedImage, setGeneratedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedModel, setSelectedModel] = useState('flux-dev');
  const [imageSize, setImageSize] = useState('landscape_16_9');
  const [inferenceSteps, setInferenceSteps] = useState(50);
  const [guidanceScale, setGuidanceScale] = useState(7.5);
  const [nsfwAllowed, setNsfwAllowed] = useState(false);
  const [nsfwDetected, setNsfwDetected] = useState(false);

  const models = [
    { value: 'flux-dev', label: 'Flux Dev' },
    { value: 'flux-schnell', label: 'Flux Schnell' },
    { value: 'sd-v3-medium', label: 'Stable Diffusion v3 Medium' },
    { value: 'flux-realism', label: 'Flux Realism' },
    { value: 'flux-lora', label: 'Flux LoRA' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setGeneratedImage(null);
    setNsfwDetected(false);

    try {
      const response = await axios.post('/api/generate-image', {
        prompt,
        model: selectedModel,
        image_size: imageSize,
        inference_steps: inferenceSteps,
        guidance_scale: guidanceScale,
        nsfw_allowed: nsfwAllowed
      });
      setGeneratedImage(response.data.image_url);
      setNsfwDetected(response.data.nsfw_detected);
      
      console.log("Full API response:", response.data);
    } catch (error) {
      console.error("Error details:", error.response?.data);
      setError(error.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-page">
      <h1 className="page-title neon-text">AI Image Generation</h1>
      <div className="content-wrapper">
        <div className="input-panel">
          <form onSubmit={handleSubmit} className="cyberpunk-form">
            <div className="form-group">
              <label htmlFor="prompt-input" className="neon-text">Prompt:</label>
              <textarea
                id="prompt-input"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe your cyberpunk vision..."
                required
                className="cyberpunk-input"
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="model-select" className="neon-text">Model:</label>
                <select
                  id="model-select"
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="cyberpunk-select"
                >
                  {models.map((model) => (
                    <option key={model.value} value={model.value}>{model.label}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="image-size" className="neon-text">Size:</label>
                <select
                  id="image-size"
                  value={imageSize}
                  onChange={(e) => setImageSize(e.target.value)}
                  className="cyberpunk-select"
                >
                  <option value="square_hd">Square HD</option>
                  <option value="square">Square</option>
                  <option value="portrait_4_3">Portrait 4:3</option>
                  <option value="portrait_16_9">Portrait 16:9</option>
                  <option value="landscape_4_3">Landscape 4:3</option>
                  <option value="landscape_16_9">Landscape 16:9</option>
                </select>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="inference-steps" className="neon-text">Inference Steps:</label>
                <input
                  type="number"
                  id="inference-steps"
                  value={inferenceSteps}
                  onChange={(e) => setInferenceSteps(Number(e.target.value))}
                  min="1"
                  max="100"
                  className="cyberpunk-input"
                />
              </div>
              <div className="form-group">
                <label htmlFor="guidance-scale" className="neon-text">Guidance Scale:</label>
                <input
                  type="number"
                  id="guidance-scale"
                  value={guidanceScale}
                  onChange={(e) => setGuidanceScale(Number(e.target.value))}
                  min="1"
                  max="20"
                  step="0.1"
                  className="cyberpunk-input"
                />
              </div>
            </div>
            <div className="form-group checkbox-group">
              <label htmlFor="nsfw-toggle" className="neon-text">
                <input
                  type="checkbox"
                  id="nsfw-toggle"
                  checked={nsfwAllowed}
                  onChange={(e) => setNsfwAllowed(e.target.checked)}
                  className="cyberpunk-checkbox"
                />
                Allow NSFW Content
              </label>
            </div>
            <button type="submit" disabled={loading} className="cyberpunk-button">
              {loading ? 'Generating...' : 'Generate Image'}
            </button>
          </form>
        </div>
        <div className="output-panel">
          {error && <div className="error neon-text">{error}</div>}
          {nsfwDetected && (
            <div className="warning neon-text">
              NSFW content may be present in the generated image.
            </div>
          )}
          {generatedImage && (
            <div className="image-container">
              <div className="large-image-display">
                <img src={generatedImage} alt="Generated" className="generated-image neon-border" />
              </div>
              <a href={generatedImage} target="_blank" rel="noopener noreferrer" className="image-link neon-text">
                View Full Image
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AIPage;