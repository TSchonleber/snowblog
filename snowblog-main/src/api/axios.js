import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://localhost:5000',  // Your Flask backend URL
  withCredentials: true
});

export default instance;