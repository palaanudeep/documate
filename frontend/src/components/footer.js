import React from 'react';
import { Container, Navbar } from 'react-bootstrap';

const Footer = () => {
  return (
    <Navbar fixed="bottom" bg="dark" variant="dark">
      <Container className="justify-content-center">
        <Navbar.Brand>
          <p>Copyright &copy; 2024</p>
        </Navbar.Brand>
      </Container>
    </Navbar>
  );
};

export default Footer;