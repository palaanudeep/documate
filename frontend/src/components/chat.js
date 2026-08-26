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
    const API_URL = process.env.REACT_APP_API_URL;
    const auth = useOutletContext();
    let location = useLocation();
    const [inputText, setInputText] = useState('');
    const [urlInput, setUrlInput] = useState('');
    const [isDocSubmitted, setIsDocSubmitted] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);
    const [messages, setMessages] = useState([]);
    const endOfMsgsRef = useRef(null);
    const [chatId, setChatId] = useState(null);
  
    const scrollToBottom = () => {
      endOfMsgsRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start"
      });
    };

    const updateChat = (newMessage='', user='', citations=[]) => {
      if (newMessage.length===0) {
        setMessages(_ => []);
        return;
      }
      setMessages(prevMessages => [...prevMessages, { message: newMessage, user, citations }]);
    };

    useEffect(() => {
      scrollToBottom();
    }, [messages, isLoading]);

    const handleInputChange = (event) => {
      const message = event.target.value;
      setInputText(message);
    };

    const handleUrlChange = (event) => {
      const url = event.target.value;
      setUrlInput(url);
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
      // Check file size (limit to 20MB)
      if (file.size > 20000000) {
        alert('File is too large. Please upload a file smaller than 20MB.');
        return;
      }
      // Set file and clear all states
      setSelectedFile(file);
      setUrlInput(''); // Clear URL when file is selected
      setIsDocSubmitted(false);
      setInputText('');
      setError(null);
      setIsLoading(false);
      // setMessages([]);
      updateChat(''); // clear chat
    };

    const makeApiCall = async () => {
      setError(null);
      setIsLoading(true);
      try {
        let response, data;
        const config = {
          headers: {
            'Authorization': `Bearer ${auth.token}`,
            'Content-Type': 'application/json'
          }
        };
        
        // Handle document/URL submission
        if ((selectedFile || urlInput) && !isDocSubmitted) {
          if (selectedFile) {
            // File upload
            const formData = new FormData();
            formData.append('file', selectedFile);
            const fileConfig = {
              headers: {
                'Authorization': `Bearer ${auth.token}`
              }
            };
            response = await axios.post(`${API_URL}/api/load_doc`, formData, fileConfig);
          } else if (urlInput) {
            // URL submission
            response = await axios.post(`${API_URL}/api/load_doc`, {
              url: urlInput
            }, config);
          }
          
          data = response.data;
          console.log('DOC/URL LOADED', data);
          setChatId(data.chat_id);
          updateChat(data.summary, '', data.citations || []);
          setIsDocSubmitted(true);
          setUrlInput(''); // Clear URL after successful load
        } else {
          // Q&A
          response = await axios.post(`${API_URL}/api/get_answer`, {
            question: inputText, 
            chat_history: messages,
            chat_id: chatId
          }, config);
          data = response.data;
          console.log('Q&A', data);
          updateChat(inputText, auth.email, []);
          updateChat(data.answer, '', data.citations || []);
        }
        setInputText('');
      } catch (error) {
        console.error(error);
        const errorMsg = error.response?.data?.message || 'An error occurred while processing the request.';
        setError(errorMsg);
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
              <Typography className="text-center" variant="h5">Submit a PDF Document or Website URL to start Q&A</Typography>
            </Paper>}
          {messages.map(({message, user, citations}, index) => (
            <Paper square key={index} className='bg-dark text-white' elevation={5} style={{ padding: '16px', marginBottom: '16px' }}>
              <Typography variant="body1">
                {user.length===0 ? (
                  <>
                    <span style={{ color: 'blue', fontSize: '24px', marginRight: '16px' }}>
                      <AiOutlineRobot />
                    </span>
                    <strong>DocuBot</strong>
                    <br />
                    <br />
                    {message}
                    {citations && citations.length > 0 && (
                      <>
                        <br />
                        <br />
                        <div style={{ fontSize: '0.85em', color: '#aaa', borderTop: '1px solid #555', paddingTop: '8px', marginTop: '8px' }}>
                          <strong>Sources:</strong>
                          {citations.map((citation, idx) => (
                            <div key={idx} style={{ marginTop: '4px', paddingLeft: '8px' }}>
                              {citation.source_type === 'url' ? (
                                <>
                                  • <a href={citation.url} target="_blank" rel="noopener noreferrer" style={{ color: '#6495ED' }}>
                                    {citation.title || citation.url}
                                  </a> (Chunk {citation.chunk_id}): "{citation.text}"
                                </>
                              ) : (
                                <>
                                  • Page {citation.page + 1}, Chunk {citation.chunk_id}: "{citation.text}"
                                </>
                              )}
                            </div>
                          ))}
                        </div>
                      </>
                    )}
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
            disabled={urlInput.length > 0}
          />
          <Button className="sm rounded-0" onClick={makeApiCall} disabled={selectedFile === null || urlInput.length > 0}>
            <UploadIcon />
          </Button>
        </InputGroup>
        <InputGroup className="my-3">
          <FormControl
            className="rounded-0"
            type="text"
            placeholder="Or paste a website URL (e.g., https://example.com/article)"
            value={urlInput}
            onChange={handleUrlChange}
            disabled={selectedFile !== null}
          />
          <Button className="sm rounded-0" onClick={makeApiCall} disabled={urlInput.trim().length === 0 || selectedFile !== null}>
            Load URL
          </Button>
        </InputGroup>
        {error && <Alert className='mb-3' variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}
        <InputGroup>
          <FormControl
            className="rounded-0"
            placeholder={isDocSubmitted  ? "Ask a Question about the source..." : "Please upload a document or URL to start Q&A"}
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