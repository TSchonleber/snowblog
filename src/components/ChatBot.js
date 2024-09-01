import React, { useState } from 'react';
import { getAIResponse } from '../ai_utils';

const ChatBot = () => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await getAIResponse(input);
        setMessages([...messages, { user: input, ai: response }]);
        setInput('');
    };

    return (
        <div className="chatbot">
            <h2>ChatBot</h2>
            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div key={index}>
                        <p>User: {msg.user}</p>
                        <p>AI: {msg.ai}</p>
                    </div>
                ))}
            </div>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask the AI..."
                />
                <button type="submit">Send</button>
            </form>
        </div>
    );
};

export default ChatBot;