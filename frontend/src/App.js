import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import Header from './components/header';
import Footer from './components/footer';
import Chat from './components/chat';
import Summarizer from './components/summarizer';
import PageNotFound from './components/pageNotFound';

import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  return (
    <Container fluid style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }} className="bg-dark text-white">
      <Router>
        <Header />
        <main className="py-3">
          <Container>
            <Routes>
              <Route path="/chat" element={<Chat/>} />
              <Route path="/summarizer" element={<Summarizer/>} />
              <Route path='*' element={<PageNotFound />} />
            </Routes>
          </Container>
        </main>
        <Footer />
      </Router>
    </Container>
  );
}

export default App;