import React from 'react';

function AboutMePage() {
  return (
    <div className="about-me-page">
      <h2>About Me</h2>
      <p>[Your about me text will go here. Feel free to add a brief introduction about yourself!]</p>
      <div className="social-links">
        <h3>Connect with me:</h3>
        <ul>
          <li><a href="https://x.com/OmniVaughn" target="_blank" rel="noopener noreferrer">Twitter</a></li>
          <li><a href="https://github.com/TSchonleber" target="_blank" rel="noopener noreferrer">GitHub</a></li>
          <li><a href="https://www.linkedin.com/in/terrence-schonleber/" target="_blank" rel="noopener noreferrer">LinkedIn</a></li>
        </ul>
      </div>
    </div>
  );
}

export default AboutMePage;