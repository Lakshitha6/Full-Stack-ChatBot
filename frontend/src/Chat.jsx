import React, {useState} from 'react'
import msg from './images/msg-Photoroom.png'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'

export default function Chat() {

const [userInput, setUserInput] = useState('');
const [chatHistory, setChatHistory] = useState([]);
const [isChatVisible, setIsChatVisible] = useState(false);

const handleInputChange = (e) => {
  setUserInput(e.target.value);
};

const handleChatVisible = () => {
  setIsChatVisible(!isChatVisible);
};

async function handleSubmit(e) {
  e.preventDefault();
  if (userInput.trim() === '') {
    return;
  }
  const newChat = {
    type: 'question',
    datas: userInput,
  };

  try{
    setChatHistory(prevHistory => [...prevHistory, newChat]);
    setUserInput('');
    const server_response = await axios.post('http://127.0.0.1:9000/chat', {prompt: newChat.datas})

    const server = {
      type: 'answer',
      datas: server_response.data.response,
    };

    setChatHistory(prevHistory => [...prevHistory, server]);

  }
  catch(error){
    alert("Error: " + error);
  }


}

  return (
    <>

      {isChatVisible && (
      <div className="chat-interface">
        <div className="msg-panel">
          {chatHistory.map((chat, index) => (
            <div key={index} className={chat.type}>
              <ReactMarkdown>{chat.datas}</ReactMarkdown>
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit}>
            <textarea
             type="text"
             placeholder='What is in your mind ?'
             className='user-input'
             value={userInput}
             onChange={handleInputChange}
            />
            <button type='submit'></button>
        </form>
      </div>
)}




      <div className="msg-box" onClick={handleChatVisible}>
        <img src={msg} alt="msg-box" className='msg-img'/>
      </div>


    </>
  )
}
