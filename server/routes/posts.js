const express = require('express');
const router = express.Router();
const Post = require('../models/Post');

// Get all posts
router.get('/', async (req, res) => {
  const posts = await Post.find().sort({ createdAt: -1 });
  res.json(posts);
});

// Create a new post
router.post('/', async (req, res) => {
  const post = new Post(req.body);
  await post.save();
  res.status(201).json(post);
});

// ... Add more routes for updating and deleting posts

module.exports = router;