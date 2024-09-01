const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const response = await axios.post('/auth/login', { username, password });
    console.log('Login response:', response);
    if (response.data.user) {
      // Handle successful login
      setUser(response.data.user);
      navigate('/');
    }
  } catch (error) {
    console.error('Login error:', error);
    // Handle login error
  }
};