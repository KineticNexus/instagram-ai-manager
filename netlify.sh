#!/bin/bash
# Simple Netlify build script for static site

# Create the dist directory
mkdir -p dist

# Copy the static content
cp -f index.html dist/index.html
cp -f netlify/_redirects dist/_redirects 2>/dev/null || echo "No redirects file found"

# Create additional static files
mkdir -p dist/css
cat > dist/css/style.css << 'EOL'
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
}

h1 {
    color: #405DE6;
}

.container {
    border: 1px solid #e1e1e1;
    border-radius: 5px;
    padding: 20px;
    margin-top: 20px;
    background: #f9f9f9;
}
EOL

# Create a status.json file
mkdir -p dist/api
cat > dist/api/status.json << 'EOL'
{
  "status": "running",
  "environment": "netlify",
  "version": "1.0.0",
  "timestamp": "2023-03-28T12:00:00Z"
}
EOL

echo "Static site build completed successfully!"