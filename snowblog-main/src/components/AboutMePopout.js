import React from 'react';
import AboutMe from './AboutMe';
import './AboutMePopout.css';

function AboutMePopout({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="about-me-overlay">
      <div className="about-me-popout">
        <button className="close-button" onClick={onClose}>×</button>
        <h2 className="glitch" data-text="About Me">About Me</h2>
        <AboutMe />
      </div>
    </div>
  );
}

export default AboutMePopout;