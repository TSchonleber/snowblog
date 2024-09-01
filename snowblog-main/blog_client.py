import requests

class BlogClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def get_posts(self):
        response = requests.get(f'{self.base_url}/api/posts')
        return response.json()

    def create_post(self, title, content, image_url=None):
        data = {
            'title': title,
            'content': content,
            'image_url': image_url
        }
        response = requests.post(f'{self.base_url}/api/posts', json=data)
        return response.json()

    def display_posts(self):
        posts = self.get_posts()
        for post in posts:
            print(f"Title: {post['title']}")
            print(f"Content: {post['content']}")
            print(f"Image URL: {post['image_url']}")
            print(f"Created at: {post['created_at']}")
            print("---")

if __name__ == '__main__':
    client = BlogClient()

    while True:
        print("\n1. View all posts")
        print("2. Create a new post")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            client.display_posts()
        elif choice == '2':
            title = input("Enter post title: ")
            content = input("Enter post content: ")
            image_url = input("Enter image URL (optional): ")
            result = client.create_post(title, content, image_url)
            print("Post created successfully!")
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")