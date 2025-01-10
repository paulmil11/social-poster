import os
import anthropic
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
import xml.etree.ElementTree as ET

# Load environment variables
load_dotenv()

class SocialPostGenerator:
    def __init__(self):
        """Initialize the generator"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.xml_path = os.getenv('WORDPRESS_XML_PATH', 'posts.xml')

    def get_blog_posts(self):
        """Fetch blog posts from WordPress XML export"""
        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            
            # Find the namespace
            ns = {'content': 'http://purl.org/rss/1.0/modules/content/',
                  'wp': 'http://wordpress.org/export/1.2/'}
            
            posts = []
            for item in root.findall('.//item'):
                try:
                    # Check if it's a published post
                    status = item.find('.//wp:status', ns)
                    post_type = item.find('.//wp:post_type', ns)
                    
                    if not (status is not None and status.text == 'publish' and 
                           post_type is not None and post_type.text == 'post'):
                        continue
                    
                    # Get content
                    content = item.find('.//content:encoded', ns)
                    if content is None:
                        continue
                    
                    title = item.find('title')
                    link = item.find('link')
                    pub_date = item.find('pubDate')
                    
                    post = {
                        'title': title.text if title is not None else 'Untitled',
                        'content': self._clean_content(content.text),
                        'url': link.text if link is not None else '',
                        'pub_date': datetime.strptime(pub_date.text, '%a, %d %b %Y %H:%M:%S %z') if pub_date is not None else datetime.now()
                    }
                    
                    # Skip posts without content or URL
                    if not post['content'].strip() or not post['url'].strip():
                        continue
                        
                    posts.append(post)
                    
                except Exception as e:
                    print(f"Error processing post: {str(e)}")
                    continue
            
            # Sort posts by publication date, newest first
            posts.sort(key=lambda x: x['pub_date'], reverse=True)
            return posts
            
        except FileNotFoundError:
            print(f"WordPress XML file not found at {self.xml_path}")
            return []
        except Exception as e:
            print(f"Error reading WordPress XML file: {str(e)}")
            return []

    def _clean_content(self, content):
        """Clean HTML content and remove extra whitespace"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            # Get text and clean whitespace
            text = ' '.join(soup.stripped_strings)
            return text
        except Exception as e:
            print(f"Error cleaning content: {str(e)}")
            return content

    def generate_social_content(self, post):
        """Generate social media content using Anthropic"""
        try:
            print(f"Attempting to generate content for post: {post['title']}")
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Create 3 social media posts about this blog post. Each post should:
- Be under 280 characters
- Include the URL at the end
- Avoid emojis, hashtags, and calls to action
- Focus on pulling compelling quotes (you dont need to put quotes around it)
- if you dont use quotes, you can slightly rephrase the content
- do not do any generic summarized takeaways

Title: {post['title']}
URL: {post['url']}
Content: {post['content'][:1500]}...

Format the posts as a numbered list."""
                    }
                ]
            )
            
            print("Raw API response:", message)
            print("Content:", message.content if hasattr(message, 'content') else "No content")
            
            # Split response into individual posts and clean them
            response_text = message.content[0].text if hasattr(message, 'content') else ""
            posts = []
            
            # Parse numbered list (1., 2., 3.)
            for line in response_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                    # Remove the number and clean up
                    post_text = line[2:].strip()
                    if post_text:
                        posts.append(post_text)
            
            # If we didn't get exactly 3 posts, return fallback content
            if len(posts) != 3:
                return [
                    f"{post['title']} {post['url']}",
                    f"New blog post: {post['title']} {post['url']}",
                    f"Latest thoughts on {post['title']} {post['url']}"
                ]
                
            return posts
            
        except Exception as e:
            print(f"Error generating social content: {str(e)}")
            return [
                f"{post['title']} {post['url']}",
                f"New blog post: {post['title']} {post['url']}",
                f"Latest thoughts on {post['title']} {post['url']}"
            ]

def main():
    # Create generator
    generator = SocialPostGenerator()
    blog_posts = generator.get_blog_posts()
    
    if not blog_posts:
        print("No posts found in WordPress XML file. Please check the file path and content.")
        return
    
    # Process the first post as an example
    first_post = blog_posts[0]
    posts = generator.generate_social_content(first_post)
    print("\nGenerated posts for:", first_post['title'])
    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post}")

if __name__ == "__main__":
    main() 