#!/usr/bin/env python
"""
Simplified build script for Netlify deployment of the Instagram AI Bot.
This creates a minimal web application without bundling heavy dependencies.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_dist_directory():
    """Create the distribution directory structure."""
    logger.info("Creating distribution directory structure")
    
    # Create dist directory if it doesn't exist
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    # Create necessary subdirectories
    static_dir = dist_dir / "static"
    static_dir.mkdir()
    
    templates_dir = dist_dir / "templates"
    templates_dir.mkdir()
    
    return dist_dir, static_dir, templates_dir

def copy_web_assets(static_dir, templates_dir):
    """Copy web assets to the distribution directory."""
    logger.info("Copying web assets")
    
    # Check if web assets exist
    if Path("web/static").exists():
        # Copy static files
        for item in Path("web/static").glob("**/*"):
            if item.is_file():
                rel_path = item.relative_to("web/static")
                dest_path = static_dir / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_path)
    else:
        logger.warning("web/static directory not found")
        
    # Copy template files
    if Path("web/templates").exists():
        for item in Path("web/templates").glob("**/*"):
            if item.is_file():
                rel_path = item.relative_to("web/templates")
                dest_path = templates_dir / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_path)
    else:
        logger.warning("web/templates directory not found")

def create_netlify_app(dist_dir):
    """Create a simplified web application for Netlify."""
    logger.info("Creating Netlify web application")
    
    # Create app.py in the dist directory
    app_content = """#!/usr/bin/env python
from flask import Flask, render_template, request, jsonify
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
"""
    
    with open(dist_dir / "app.py", "w") as f:
        f.write(app_content)
    
    # Create a simple index.html if it doesn't exist
    if not (dist_dir / "templates" / "index.html").exists():
        with open(dist_dir / "templates" / "index.html", "w") as f:
            f.write("""<!DOCTYPE html>
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
    <p>Access the API endpoints to interact with the bot.</p>
</body>
</html>""")

def create_netlify_config_files(dist_dir):
    """Create necessary configuration files for Netlify."""
    logger.info("Creating Netlify configuration files")
    
    # Create runtime.txt
    with open(dist_dir / "runtime.txt", "w") as f:
        f.write("python-3.8")
    
    # Create requirements.txt with minimal dependencies
    with open(dist_dir / "requirements.txt", "w") as f:
        f.write("""flask==2.0.1
gunicorn==20.1.0
requests==2.28.1
python-dotenv==0.19.2
Pillow==9.5.0
werkzeug==2.0.2
itsdangerous==2.0.1
jinja2==3.0.3
click==8.0.3
""")
    
    # Create Procfile for web server
    with open(dist_dir / "Procfile", "w") as f:
        f.write("web: gunicorn app:app")

def main():
    """Main build function."""
    try:
        logger.info("Starting Netlify build process")
        
        # Create directory structure
        dist_dir, static_dir, templates_dir = create_dist_directory()
        
        # Copy web assets
        copy_web_assets(static_dir, templates_dir)
        
        # Create simplified web application
        create_netlify_app(dist_dir)
        
        # Create configuration files
        create_netlify_config_files(dist_dir)
        
        logger.info("Netlify build completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Build failed: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())