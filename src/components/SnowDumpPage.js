import React, { useState, useEffect } from 'react';
import { getAIResponse } from '../ai_utils';

const SnowDumpPage = () => {
    const [aiResponse, setAIResponse] = useState('');

    useEffect(() => {
        const fetchAIResponse = async () => {
            const response = await getAIResponse('Tell me about snow dumps');
            setAIResponse(response);
        };
        fetchAIResponse();
    }, []);

    return (
        <div>
            <h1>Snow Dump</h1>
            <p>{aiResponse}</p>
            {/* Add any other snow dump content here */}
        </div>
    );
};

export default SnowDumpPage;