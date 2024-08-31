const express = require('express');
const mongoose = require('mongoose');
const postRoutes = require('./routes/posts');

const app = express();
const PORT = process.env.PORT || 5000;

// Connect to MongoDB
mongoose.connect('mongodb://localhost/blog_db', { useNewUrlParser: true, useUnifiedTopology: true });

app.use(express.json());
app.use('/api/posts', postRoutes);

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));