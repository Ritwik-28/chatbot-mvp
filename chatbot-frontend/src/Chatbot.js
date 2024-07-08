import React, { useState } from 'react';
import axios from 'axios';
import './Chatbot.css';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (input.trim() === '') return;

    const newMessage = { sender: 'user', message: input };
    setMessages([...messages, newMessage]);

    try {
      const response = await axios.post(
        'http://localhost:5055/webhook', 
        {
          sender: 'user',
          message: input
        }, 
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      console.log('Response data:', response.data);
      
      const botMessages = response.data.map(botMessage => {
        const messageText = botMessage.text;
        const youtubeUrl = extractYouTubeUrl(messageText);
        return youtubeUrl
          ? { sender: 'bot', message: messageText, youtubeUrl: youtubeUrl }
          : { sender: 'bot', message: messageText };
      });
      
      setMessages(prevMessages => [...prevMessages, ...botMessages]);
    } catch (error) {
      console.error('Error sending message:', error);
      if (error.response) {
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
      }
      setMessages(prevMessages => [
        ...prevMessages,
        { sender: 'bot', message: "Sorry, I'm having trouble connecting. Please try again later." }
      ]);
    }

    setInput('');
  };

  const extractYouTubeUrl = (text) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const urls = text.match(urlRegex);
    if (urls) {
      const youtubeUrl = urls.find(url => url.includes('youtube.com') || url.includes('youtu.be'));
      return youtubeUrl;
    }
    return null;
  };

  const handleInputChange = (event) => {
    setInput(event.target.value);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className="chatbot">
      <div className="chatbot-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <p>{msg.message}</p>
            {msg.buttons && (
              <div className="button-container">
                {msg.buttons.map((button, btnIndex) => (
                  <button key={btnIndex} onClick={() => setInput(button.payload)}>
                    {button.title}
                  </button>
                ))}
              </div>
            )}
            {msg.youtubeUrl && (
              <div className="youtube-video">
                <iframe
                  title={`YouTube video ${index}`}
                  width="560"
                  height="315"
                  src={msg.youtubeUrl}
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="chatbot-input">
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder="Hi, how can we help you?"
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default Chatbot;