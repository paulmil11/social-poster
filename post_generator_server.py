from flask import Flask, render_template, request, jsonify
from social_post_generator import SocialPostGenerator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure required environment variables are set
if not os.getenv('ANTHROPIC_API_KEY'):
    raise EnvironmentError("ANTHROPIC_API_KEY must be set in .env file")
if not os.getenv('WORDPRESS_XML_PATH'):
    raise EnvironmentError("WORDPRESS_XML_PATH must be set in .env file")

app = Flask(__name__)
generator = SocialPostGenerator()

@app.route('/')
def home():
    try:
        # Get all blog posts
        posts = generator.get_blog_posts()
        if not posts:
            return render_template('index.html', posts=[], error="No posts found in WordPress XML file")
        return render_template('index.html', posts=posts)
    except Exception as e:
        print(f"Error loading posts: {str(e)}")
        return render_template('index.html', posts=[], error=str(e))

@app.route('/generate', methods=['POST'])
def generate_posts():
    try:
        post_title = request.json.get('title')
        if not post_title:
            return jsonify({'error': 'No post title provided'}), 400
        
        posts = generator.get_blog_posts()
        if not posts:
            return jsonify({'error': 'No posts found in WordPress XML file'}), 404
        
        # Find the selected post
        selected_post = next((post for post in posts if post['title'] == post_title), None)
        if not selected_post:
            return jsonify({'error': 'Selected post not found'}), 404
        
        # Generate posts
        generated_posts = generator.generate_social_content(selected_post)
        if not generated_posts:
            return jsonify({'error': 'Failed to generate posts'}), 500
        
        return jsonify({'posts': generated_posts})
        
    except Exception as e:
        print(f"Error generating posts: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 