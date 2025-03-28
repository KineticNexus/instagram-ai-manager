#!/bin/bash
# Simple Netlify build script

# Create the dist directory
mkdir -p dist
mkdir -p dist/templates
mkdir -p dist/static

# Create a simple index.html
cat > dist/templates/index.html << 'EOL'
<!DOCTYPE html>
<html>
<head>
    <title>Instagram AI Bot</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #405DE6; }
    </style>
</head>
<body>
    <h1>Instagram AI Bot</h1>
    <p>The Instagram AI Bot is running on Netlify.</p>
    <p>This is a simplified deployment for demonstration purposes.</p>
</body>
</html>
EOL

# Create a simple app.py
cat > dist/app.py << 'EOL'
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({"status": "running", "environment": "netlify"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
EOL

# Create Procfile
cat > dist/Procfile << 'EOL'
web: gunicorn app:app
EOL

# Create requirements.txt
cat > dist/requirements.txt << 'EOL'
flask==2.0.1
gunicorn==20.1.0
Werkzeug==2.0.2
Jinja2==3.0.3
itsdangerous==2.0.1
click==8.0.3
EOL

# Create runtime.txt
echo "python-3.8" > dist/runtime.txt

# Copy netlify redirects
cp -f netlify/_redirects dist/_redirects || echo "No redirects file found"

echo "Build completed successfully!"