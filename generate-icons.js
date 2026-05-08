// Run with: node generate-icons.js
// Generates icon-192.png and icon-512.png using pure SVG->PNG via sharp or jimp

const fs = require('fs');

// Create SVG icon
function makeSVG(size) {
  const fontSize = Math.round(size * 0.52);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a0f1e"/>
      <stop offset="100%" style="stop-color:#1a2235"/>
    </linearGradient>
    <linearGradient id="ring" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#ffd700"/>
      <stop offset="100%" style="stop-color:#f59e0b"/>
    </linearGradient>
  </defs>
  <rect width="${size}" height="${size}" rx="${size*0.22}" fill="url(#bg)"/>
  <rect x="${size*0.04}" y="${size*0.04}" width="${size*0.92}" height="${size*0.92}" rx="${size*0.18}" fill="none" stroke="url(#ring)" stroke-width="${size*0.04}"/>
  <text x="50%" y="55%" font-size="${fontSize}" text-anchor="middle" dominant-baseline="middle" font-family="Arial">🎰</text>
  <text x="50%" y="82%" font-size="${Math.round(size*0.1)}" text-anchor="middle" font-family="Arial,sans-serif" fill="#ffd700" font-weight="900">B60</text>
</svg>`;
}

// Write SVG files (these work as icons too, and we'll convert in Dockerfile)
fs.writeFileSync('icon-192.svg', makeSVG(192));
fs.writeFileSync('icon-512.svg', makeSVG(512));
console.log('SVG icons generated');
