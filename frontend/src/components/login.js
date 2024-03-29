import React, {useState} from 'react';
import axios from 'axios';
import { Alert, Button, Container, Form, Spinner } from 'react-bootstrap';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Typography } from '@mui/material';


function LoginForm({login}) {
    let location = useLocation();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [state , setState] = useState({
        email : "",
        password : "",
        errorMessage: null
    })
    const handleChange = (e) => {
        const {id , value} = e.target   
        setState(prevState => ({
            ...prevState,
            [id] : value
        }))
    }

    const submitLogin = async (event) => {
        event.preventDefault();
        setLoading(true);
        try {
            const response = await axios.post('/api/login', {
                email: state.email,
                password: state.password
            });
            const data = response.data;
            console.log(data);
            login({
                email: data.email,
                token: data.access_token
            });
            navigate('/', { state: { message: 'Login successful. Welcome back!' } });
            setLoading(false);
        } catch (error) {
            console.error('Error:', error);
            setState(prevState => ({
                ...prevState,
                'errorMessage' : 'Login failed. Please try again.'
            }));
            setLoading(false);
        }
    }
    
    
    return(
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
            <Container className="d-flex flex-column align-items-stretch border border-light pt-3" style={{ minHeight: '50vh', width: '30vw'}}>
                {location.state && location.state.message && (
                    <Alert variant="success" dismissible>
                        {location.state.message}
                    </Alert>
                )}
                <Typography variant="h4" component="h1" gutterBottom align="center">
                    Login
                </Typography>
                {loading ? (
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                        <Spinner animation="border" />
                    </div>
                ) : (
                    <Form onSubmit={submitLogin}>
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
                        <Button 
                            variant="primary" 
                            type="submit" 
                            className="rounded-0"
                            disabled={!state.email || !state.password }
                        >
                            Login
                        </Button>
                        {state.errorMessage && <Alert variant="danger" className="mt-2 py-0 px-1 rounded-0" size="sm">{state.errorMessage}</Alert>}
                        <div className="mt-3">
                            <span>Dont have an account? </span>
                            <Link variant="dark" to="/register" size="md">Register</Link>
                        </div>
                    </Form>
                )}
            </Container>
        </div>
    )
}

export default LoginForm;