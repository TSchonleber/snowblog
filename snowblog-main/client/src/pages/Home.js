import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Home() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetch('/api/posts')
      .then(res => res.json())
      .then(data => setPosts(data));
  }, []);

  return (
    <div>
      <h1>My Blog</h1>
      {posts.map(post => (
        <div key={post._id}>
          <h2><Link to={`/post/${post._id}`}>{post.title}</Link></h2>
          <p>{post.content.substring(0, 100)}...</p>
          {post.imageUrl && <img src={post.imageUrl} alt={post.title} style={{maxWidth: '300px'}} />}
        </div>
      ))}
    </div>
  );
}

export default Home;