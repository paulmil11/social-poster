# Social Post Generator

A simple web app that generates social media posts from your blog content using AI.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/social-post-generator.git
cd social-post-generator
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
ANTHROPIC_API_KEY=your_api_key_here
WORDPRESS_XML_PATH=posts.xml
```

4. Add your WordPress XML export file as `posts.xml` in the root directory

## Running the App

1. Start the Flask server:
```bash
python post_generator_server.py
```

2. Open your browser and visit `http://127.0.0.1:5001`

## Features

- Generate social media posts from your blog content using AI
- One-click posting to X (Twitter) and Threads
- Random post selection
- Clean, simple interface

## Requirements

- Python 3.7+
- Anthropic API key
- WordPress XML export file
