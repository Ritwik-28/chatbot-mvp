import React, { useState } from 'react';
import axios from 'axios';
import Modal from 'react-modal';
import './Chatbot.css';

Modal.setAppElement('#root');

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [videoUrl, setVideoUrl] = useState('');

  const sendMessage = async () => {
    if (input.trim() === '') return;

    const newMessage = { sender: 'user', message: input };
    setMessages([...messages, newMessage]);

    try {
      const response = await axios.post('http://localhost:5055/webhook', {
        sender: 'user',
        message: input
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('Response data:', response.data);

      if (response.data && Array.isArray(response.data)) {
        const botMessages = response.data.map(botMessage => {
          const messageText = botMessage.text;
          const youtubeUrl = extractYouTubeUrl(messageText);
          return youtubeUrl
            ? { sender: 'bot', message: messageText, youtubeUrl: youtubeUrl }
            : { sender: 'bot', message: messageText, buttons: botMessage.buttons || [] };
        });
        setMessages(prevMessages => [...prevMessages, ...botMessages]);
      } else if (response.data.responses && response.data.responses.length > 0) {
        const fallbackMessage = response.data.responses[0].text;
        setMessages(prevMessages => [
          ...prevMessages,
          { sender: 'bot', message: fallbackMessage }
        ]);
      } else {
        setMessages(prevMessages => [
          ...prevMessages,
          { sender: 'bot', message: "Sorry, I'm having trouble understanding your request." }
        ]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
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

  const openModal = (url) => {
    setVideoUrl(url);
    setModalIsOpen(true);
  };

  const closeModal = () => {
    setModalIsOpen(false);
    setVideoUrl('');
  };

  const handleButtonClick = (payload) => {
    setInput(payload);
    sendMessage();
  };

  return (
    <div className="chatbot">
      <div className="chatbot-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <p>{msg.message}</p>
            {msg.youtubeUrl && (
              <button onClick={() => openModal(msg.youtubeUrl)}>Play Video</button>
            )}
            {msg.buttons && msg.buttons.length > 0 && (
              <div className="button-container">
                {msg.buttons.map((button, btnIndex) => (
                  <button key={btnIndex} onClick={() => handleButtonClick(button.payload)}>
                    {button.title}
                  </button>
                ))}
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
          placeholder="Type a message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        contentLabel="YouTube Video"
        className="modal"
        overlayClassName="overlay"
      >
        <button onClick={closeModal} className="close-button">Close</button>
        <iframe
          title="YouTube video"
          width="560"
          height="315"
          src={videoUrl}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        ></iframe>
      </Modal>
    </div>
  );
};

export default Chatbot;