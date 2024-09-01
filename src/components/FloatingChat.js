import React, { useState, useEffect, useRef } from 'react';
import api from '../api/axios';

function FloatingChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [isLoading, setIsLoading] = useState(false);
  const chatMessagesRef = useRef(null);

  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    setIsLoading(true);
    const userMessage = { role: 'user', content: message };
    setChatHistory(prev => [...prev, userMessage]);
    setMessage('');

    try {
      console.log('Sending request to /api/ai/text with:', { message, model: selectedModel });
      const response = await api.post('/api/ai/text', { message, model: selectedModel });
      console.log('Received response:', response.data);
      const aiMessage = { role: 'ai', content: response.data.response };
      setChatHistory(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      console.error('Error details:', error.response?.data);
      const errorMessage = { role: 'error', content: `Failed to get response. Error: ${error.response?.data?.error || error.message}` };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className={`floating-chat ${isOpen ? 'open' : ''} ${isExpanded ? 'expanded' : ''}`}>
      <button className="chat-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? 'Close Chat' : 'Open Chat'}
      </button>
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              <option value="gpt-4o">GPT-4O</option>
              <option value="chatgpt-4o-latest">ChatGPT-4O Latest</option>
              <option value="gpt-4o-mini">GPT-4O Mini</option>
            </select>
            <button className="expand-button" onClick={toggleExpand}>
              {isExpanded ? 'Minimize' : 'Expand'}
            </button>
          </div>
          <div className="chat-messages" ref={chatMessagesRef}>
            {chatHistory.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {isLoading && <div className="message loading">AI is thinking...</div>}
          </div>
          <form onSubmit={handleSubmit} className="chat-input">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default FloatingChat;