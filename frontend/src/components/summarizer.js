import React, { useState } from 'react';
import { Container, Typography, Paper } from '@mui/material';
import { Button, FormControl, InputGroup, Spinner, Alert } from 'react-bootstrap';

function Summarizer() {
    const [inputText, setInputText] = useState('');
    const [responseText, setResponseText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);
  
    const handleInputChange = (event) => {
      setInputText(event.target.value);
      console.log('input changed to: ', event.target.value);
      setSelectedFile(null);
    };
  
    const handleFileUpload = (event) => {
      const acceptedFileTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      const file = event.target.files[0];
      // Check file type
      if (file && !acceptedFileTypes.includes(file.type)) {
        alert('Invalid file type. Please upload a PDF, DOCX, or TXT file.');
        return;
      }
      // Check file size (limit to 1MB for example)
      if (file.size > 1000000) {
        alert('File is too large. Please upload a file smaller than 1MB.');
        return;
      }
      setSelectedFile(file);
      setInputText('');
    };

    const makeApiCall = async () => {
      setError(null);
      setIsLoading(true);
      try {
        let response;
        if (selectedFile) {
          const formData = new FormData();
          formData.append('file', selectedFile);
          response = await fetch('http://localhost:5000/summarize', {
            method: 'POST',
            body: formData
          });
        } else {
          response = await fetch('http://localhost:5000/summarize', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: inputText })
          });
        }
        const data = await response.json();
        console.log('RESPONSE', data);
        setResponseText(data.summary);
      } catch (error) {
        console.error(error);
        setError('An error occurred while summarizing the text.');
      } finally {
        setIsLoading(false);
      }
    };
  
    return (
      isLoading ? 
      (<Container>
        <Spinner animation="border" />
      </Container>) :
      (<Container>
        <InputGroup className="mb-3">
          <FormControl
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileUpload}
          />
        </InputGroup>
        <InputGroup>
          <FormControl
            as="textarea"
            value={inputText}
            onChange={handleInputChange}
          />
          <Button size='sm' onClick={makeApiCall}>Summarize</Button>
        </InputGroup>
        {error && <Alert variant="danger">{error}</Alert>}
        <Paper elevation={3} style={{ padding: '16px', marginTop: '16px' }}>
          <Typography variant="body1">{responseText}</Typography>
        </Paper>
      </Container>)
    );
  }
  
  export default Summarizer;