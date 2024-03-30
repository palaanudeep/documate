import React from 'react';
import { Navbar, Nav } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { Link } from 'react-router-dom';

const Header = ({logout}) => {

  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <LinkContainer to="/">
        <Navbar.Brand className="mx-auto"><strong>DocuMate</strong></Navbar.Brand>
      </LinkContainer>
      {/*<Navbar.Toggle aria-controls="basic-navbar-nav" />
      <Navbar.Collapse id="basic-navbar-nav" className="justify-content-center">
        <Nav className="ml-auto">
          <LinkContainer to="/summarizer">
            <Nav.Link>Summarizer</Nav.Link>
          </LinkContainer>
          <LinkContainer to="/chat">
            <Nav.Link>Chat</Nav.Link>
          </LinkContainer>
        </Nav>
      </Navbar.Collapse>*/}
      {logout && <Nav className="ml-auto">
        <Nav.Link as={Link} onClick={logout} to="/">Logout</Nav.Link>
      </Nav>}
    </Navbar>
  );
};

export default Header;