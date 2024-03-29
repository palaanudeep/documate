import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Container, Typography, Paper } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import UploadIcon from '@mui/icons-material/Upload';
import { Button, FormControl, InputGroup, Spinner, Alert } from 'react-bootstrap';
import { AiOutlineRobot } from 'react-icons/ai'; // for bot messages
import { FaUser } from 'react-icons/fa'; // for user messages
import { useLocation, useOutletContext } from 'react-router-dom';

function Chat() {
    const auth = useOutletContext();
    let location = useLocation();
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
      const acceptedFileTypes = ['application/pdf'];
      const file = event.target.files[0];
      if (!file) {
        return;
      }
      // Check file type
      if (!acceptedFileTypes.includes(file.type)) {
        alert('Invalid file type. Please upload a PDF file.');
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
        const config = {
          headers: {
            'Authorization': `Bearer ${auth.token}`
          }
        };
        if (selectedFile && !isDocSubmitted) {
          const formData = new FormData();
          formData.append('file', selectedFile);
          response = await axios.post('/api/load_doc', formData, config);
          data = response.data;
          console.log('DOC LOADED', data);
          setMessages([...messages, data.message]);
          setIsDocSubmitted(true);
        } else {
          response = await axios.post('/api/get_answer', {
            question: inputText, 
            chat_history: messages
          }, config);
          data = response.data;
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
          {location.state && location.state.message && (
              <Alert variant="success" dismissible>
                  {location.state.message}
              </Alert>
            )}
          {messages && messages.length===0 && 
            <Paper square className='bg-dark text-white' elevation={3} style={{ padding: '16px', marginBottom: '16px' }}>
              <Typography className="text-center" variant="h5">Submit a PDF Document to start the Q&A Chatbot</Typography>
            </Paper>}
          {messages.map((message, index) => (
            <Paper square key={index} className='bg-dark text-white' elevation={5} style={{ padding: '16px', marginBottom: '16px' }}>
              <Typography variant="body1">
                {index%2===0 ? (
                  <>
                    <span style={{ color: 'blue', fontSize: '24px', marginRight: '16px' }}>
                      <AiOutlineRobot />
                    </span>
                    <strong>DocuBot</strong>
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
                    <strong>User ({auth.email})</strong>
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
            accept=".pdf"
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