import React from 'react';
import AboutMe from './AboutMe';
import './AboutMePopout.css';

function AboutMePopout({ isOpen, onClose }) {
  return (
    <div className={`about-me-popout ${isOpen ? 'open' : ''}`}>
      <div className="about-me-content">
        <button className="close-button" onClick={onClose}>×</button>
        <AboutMe />
      </div>
    </div>
  );
}

export default AboutMePopout;