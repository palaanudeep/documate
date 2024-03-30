import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Alert, Button, Container, Form, Spinner } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { Typography } from '@mui/material';


function RegistrationForm() {
    const API_URL = process.env.REACT_APP_API_URL;
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [state , setState] = useState({
        email : "",
        password : "",
        confirmPassword: "",
        errorMessage: null
    })
    const [passwordMatch, setPasswordMatch] = useState(null);

    useEffect(() => {
        if (state.password && state.confirmPassword) {
            if (state.password === state.confirmPassword) {
                setPasswordMatch(true);
            } else {
                setPasswordMatch(false);
            }
        } else {
            setPasswordMatch(null);
        }
    }, [state.password, state.confirmPassword]);

    const handleChange = (e) => {
        const {id , value} = e.target
        setState(prevState => ({
            ...prevState,
            [id] : value
        }))
    }
    
    const submitRegistraion = async (event) => {
        event.preventDefault();
        setLoading(true);
        try {
            const response = await axios.post(`${API_URL}/api/register`, {
                email: state.email,
                password: state.password
            });
            const data = response.data;
            console.log(data);
            navigate('/login', { state: { message: 'Registration successful. Please login to continue.' } });
            setLoading(false);
        } catch (error) {
            console.error('Error:', error);
            setState(prevState => ({
                ...prevState,
                'errorMessage' : 'Registration failed. Please try again.'
            }));
            setLoading(false);
        }
    }

    return (
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '70vh' }}>
            <Container className="d-flex flex-column align-items-stretch border border-light pt-3" style={{ minHeight: '60vh', width: '30vw'}}>
                <Typography variant="h4" component="h1" gutterBottom align="center">
                    Register
                </Typography>
                {loading ? (
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                        <Spinner animation="border" />
                    </div>
                ) : (
                    <Form onSubmit={submitRegistraion}>
                        <Form.Group className="mb-3 text-left">
                            <Form.Label>Email address</Form.Label>
                            <Form.Control 
                                type="email"
                                id="email"
                                placeholder="Enter email"
                                value={state.email}
                                onChange={handleChange}
                                className="rounded-0"
                            />
                        </Form.Group>
                        <Form.Group className="mb-3 text-left">
                            <Form.Label>Password</Form.Label>
                            <Form.Control 
                                type="password"
                                id="password"
                                placeholder="Password"
                                value={state.password}
                                onChange={handleChange}
                                className="rounded-0"
                            />
                        </Form.Group>
                        <Form.Group className="mb-3 text-left">
                            <Form.Label>Confirm Password</Form.Label>
                            <Form.Control 
                                type="password"
                                id="confirmPassword"
                                placeholder="Confirm Password"
                                value={state.confirmPassword}
                                onChange={handleChange}
                                className="rounded-0"
                            />
                            {passwordMatch === false && <Alert variant="danger" className="mt-2 py-0 px-1 rounded-0" size="sm">Passwords do not match</Alert>}
                            {passwordMatch === true && <Alert variant="success" className="mt-2 py-0 px-1 rounded-0" size="sm">Passwords match</Alert>}
                        </Form.Group>
                        <Button 
                            variant="primary" 
                            type="submit" 
                            className="rounded-0"
                            disabled={!state.email || !state.password || !state.confirmPassword || state.password !== state.confirmPassword}
                        >
                            Register
                        </Button>
                        {state.errorMessage && <Alert variant="danger" className="mt-2 py-0 px-1 rounded-0" size="sm">{state.errorMessage}</Alert>}
                        <div className="mt-3">
                            <span>Already have an account? </span>
                            <Link variant="dark" to="/login" size="md">Login</Link>
                        </div>
                    </Form>
                )}
            </Container>
        </div>
    )
}

export default RegistrationForm;