# Instagram AI Bot for Kinetic Nexus

An automated Instagram bot that generates and posts professional content about international business intelligence and market analysis for Kinetic Nexus.

## Features

- 🤖 AI-powered content generation using OpenAI and Midjourney
- 🖼️ Professional business visuals and infographics
- 📊 Market analysis and business intelligence content
- 🌐 International trade and export focused
- 📱 Web interface for easy management
- 📈 Analytics and performance tracking
- ⏱️ Automated posting scheduler

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
5. Start the web interface:
   ```bash
   python src/web_interface/app.py
   ```

## Environment Variables

Required environment variables:
- `INSTAGRAM_USERNAME`: Your Instagram username
- `INSTAGRAM_PASSWORD`: Your Instagram password
- `OPENAI_API_KEY`: OpenAI API key for content generation
- `MIDJOURNEY_API_KEY`: Midjourney API key for image generation

Optional:
- `PORT`: Web interface port (default: 5000)
- `PROXY`: HTTP/HTTPS proxy if needed

## Security

- Never commit your `.env` file
- Keep your API keys and credentials secure
- Use environment variables for sensitive data
- The repository includes proper `.gitignore` rules

## License

Private repository - All rights reserved

## Quick Start

### One-Click Launcher

1. Make sure you have Python and Node.js installed
2. Double-click `start_instagram_bot.bat` to launch the application
3. The web interface will open in your default browser
4. Log in with your Instagram credentials
5. Start generating and posting content!

### Requirements

- Python 3.8 or higher
- Node.js 14 or higher
- Instagram account
- OpenAI API key
- Midjourney API key (from GoAPI.ai)

### Configuration

1. Copy `.env.example` to `.env`
2. Edit `.env` and add your API keys and Instagram credentials:

```
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
OPENAI_API_KEY=your_openai_api_key
MIDJOURNEY_API_KEY=your_midjourney_api_key
```

## Creating a Standalone Executable

To create a standalone executable that can be run from a USB drive:

1. Make sure you have Python installed
2. Run the build script:

```
python build_standalone.py
```

3. The standalone application will be created in the `dist` directory
4. Copy the entire `dist` directory to your USB drive or any location
5. Run the application using the launcher script in the `dist` directory

## Deploying to Netlify

The Instagram AI Bot can be deployed to Netlify for cloud-based access:

1. Fork or clone this repository
2. Sign up for a Netlify account if you don't have one
3. Create a new site from Git in the Netlify dashboard
4. Connect to your GitHub repository
5. Set the build settings automatically (they will be loaded from `netlify.toml`)
6. Add the required environment variables in the Netlify dashboard:
   - `INSTAGRAM_USERNAME`
   - `INSTAGRAM_PASSWORD`
   - `OPENAI_API_KEY`
   - `MIDJOURNEY_API_KEY`
7. Deploy your site

The deployment includes:
- A simplified web interface accessible from any device
- REST API endpoints for bot control
- Automatic updates when you push changes to the repository

### Troubleshooting Netlify Deployment

If you encounter issues with the deployment:

1. Check the build logs in the Netlify dashboard
2. Ensure all environment variables are correctly set
3. Try deploying with the simplified requirements by using:
   ```
   pip install -r requirements-netlify.txt
   ```
4. For Python package build issues, check that the correct version of Pillow is specified in `requirements-netlify.txt`

## Manual Startup

If you prefer to start the components manually:

1. Start the browser tools server:
```
node src/browser_tools/mcp_server.js
```

2. Start the web interface:
```
python src/web_interface/app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Troubleshooting

- **Missing dependencies**: Run `pip install -r requirements.txt` to install all required Python packages
- **Browser tools error**: Make sure Node.js is installed and the browser tools server is running
- **Instagram login issues**: Check your credentials in the `.env` file
- **API key errors**: Verify your OpenAI and Midjourney API keys are valid

## Browser Tools Integration

This project includes integration with Browser Tools MCP, which allows for browser automation and debugging. The integration enables:

- Console logging and error monitoring
- Network request tracking
- Screenshot capture
- DOM element interaction

### Testing Browser Tools

To test the browser tools integration:

1. Start the Flask application: `python src/run.py`
2. Navigate to `http://localhost:5000/login` and log in
3. Visit the test pages:
   - `/image-test` - Test image generation and display
   - `/browser-tools-test` - Test browser tools functionality

For detailed setup instructions, see the [Browser Tools Setup Guide](BROWSER_TOOLS_SETUP.md).