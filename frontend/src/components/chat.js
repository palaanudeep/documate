import React, { useState, useRef, useEffect } from 'react';
import { Container, Typography, Paper } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import UploadIcon from '@mui/icons-material/Upload';
import { Button, FormControl, InputGroup, Spinner, Alert } from 'react-bootstrap';
import { AiOutlineRobot } from 'react-icons/ai'; // for bot messages
import { FaUser } from 'react-icons/fa'; // for user messages

function Chat() {
    const [inputText, setInputText] = useState('');
    const [isDocSubmitted, setIsDocSubmitted] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);
    const [messages, setMessages] = useState([]);
    const endOfMsgsRef = useRef(null);
  
    const scrollToBottom = () => {
      endOfMsgsRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start"
      });
    };

    useEffect(() => {
      scrollToBottom();
    }, [messages, isLoading]);

    const handleInputChange = (event) => {
      setInputText(event.target.value);
    };
  
    const handleFileUpload = (event) => {
      const acceptedFileTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      const file = event.target.files[0];
      if (!file) {
        return;
      }
      // Check file type
      if (!acceptedFileTypes.includes(file.type)) {
        alert('Invalid file type. Please upload a PDF, DOCX, or TXT file.');
        return;
      }
      // Check file size (limit to 1MB for example)
      if (file.size > 10000000) {
        alert('File is too large. Please upload a file smaller than 10MB.');
        return;
      }
      // Set file and clear all states
      setSelectedFile(file);
      setIsDocSubmitted(false);
      setInputText('');
      setError(null);
      setIsLoading(false);
      setMessages([]);
    };

    const makeApiCall = async () => {
      setError(null);
      setIsLoading(true);
      try {
        let response, data;
        if (selectedFile && !isDocSubmitted) {
          const formData = new FormData();
          formData.append('file', selectedFile);
          response = await fetch('http://localhost:5000/load_doc', {
            method: 'POST',
            body: formData
          });
          data = await response.json();
          console.log('DOC LOADED', data);
          setMessages([...messages, data.message]);
          setIsDocSubmitted(true);
        } else {
          response = await fetch('http://localhost:5000/get_answer', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: inputText, chat_history: messages})
          });
          data = await response.json();
          console.log('Q&A', data);
          setMessages([...messages, `${inputText}`, data.answer]);
        }
        setInputText('');
      } catch (error) {
        console.error(error);
        setError('An error occurred while processing the text.');
      } finally {
        setSelectedFile(null);
        setIsLoading(false);
        scrollToBottom();
      }
    };
  
    return (
      <Container>
        <div className="d-flex justify-content-center align-items-center vh-50">
          <Container className="border border-light overflow-auto pt-3" style={{ height: '65vh', width: '60vw'}}>
          {messages && messages.length===0 && 
            <Paper square className='bg-dark text-white' elevation={3} style={{ padding: '16px', marginBottom: '16px' }}>
              <Typography className="text-center" variant="h5">Submit a Document (PDF, DOCX, TXT) to start the Q&A Chatbot</Typography>
            </Paper>}
          {messages.map((message, index) => (
            <Paper square key={index} className='bg-dark text-white' elevation={5} style={{ padding: '16px', marginBottom: '16px' }}>
              <Typography variant="body1">
                {index%2===0 ? (
                  <>
                    <span style={{ color: 'blue', fontSize: '24px', marginRight: '16px' }}>
                      <AiOutlineRobot />
                    </span>
                    <strong>CHATBOT</strong>
                    <br />
                    <br />
                    {message}
                    <br />
                    <br />
                    Feel free to ask any follow-up questions.
                  </>
                ) : (
                  <>
                    <span style={{ color: 'green', fontSize: '24px', marginRight: '16px' }}>
                      <FaUser />
                    </span>
                    <strong>USER</strong>
                    <br />
                    <br />
                    {message}
                  </>
                )}
              </Typography>
            </Paper>
          ))}
          {isLoading && 
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
              <Spinner animation="border" />
            </div>
          }
            <div className='mb-2' ref={endOfMsgsRef}/>
          </Container>
        </div>
        <InputGroup className="my-3">
          <FormControl
            className="rounded-0"
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileUpload}
          />
          <Button className="sm rounded-0" onClick={makeApiCall} disabled={selectedFile === null}>
            <UploadIcon />
          </Button>
        </InputGroup>
        {error && <Alert className='mb-3' variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}
        <InputGroup>
          <FormControl
            className="rounded-0"
            placeholder={isDocSubmitted  ? "Ask a Question about the document..." : "Please upload a document to start Q&A"}
            as="textarea"
            value={inputText}
            onChange={handleInputChange}
            disabled={!isDocSubmitted || isLoading}
          />
          <Button className="sm rounded-0" onClick={makeApiCall} disabled={!isDocSubmitted || (inputText.length===0)}>
            <SendIcon />
          </Button>
        </InputGroup>
      </Container>
    );
  }
  
  export default Chat;