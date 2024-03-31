import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Outlet } from 'react-router-dom';
import { useCookies } from "react-cookie";
import { Container } from 'react-bootstrap';
import Header from './components/header';
import Footer from './components/footer';
import Chat from './components/chat';
import Register from './components/register';
import Login from './components/login';
// import Summarizer from './components/summarizer';
import PageNotFound from './components/pageNotFound';

import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

const PublicRoute = ({ auth, redirectPath = "/" }) => {
  if (auth && auth.token && auth.token.length !== 0) {
    return <Navigate to={redirectPath} replace />;
  }
  return (
    <div>
      <Header />
      <main className="py-3">
        <Outlet />
      </main>
    </div>
  );
};

const PrivateRoute = ({ auth, redirectPath = "/login", logout }) => {
  if (!auth || !auth.token) {
    return <Navigate to={redirectPath} replace />;
  }
  return (
    <div>
      <Header logout={logout} />
      <main className="py-3">
        <Outlet context={auth} />
      </main>
    </div>
  );
};


function App() {
  const authCookie = "user";
  const [cookies, setCookie, removeCookie] = useCookies([authCookie]);

  const setAuthData = (authData) => {
    console.log("all cookies", cookies);
    console.log("authData", authData);
    setCookie(authCookie, authData, { path: "/" });
  };

  const removeAuthData = () => {
    console.log("all cookies", cookies);
    console.log(authCookie);
    removeCookie(authCookie, { path: "/" });
    console.log("cookies after delete", cookies);
  };

  return (
    <Container fluid style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }} className="bg-dark text-white">
      <Router>
        <Container>
          <Routes>
            <Route element={<PublicRoute auth={cookies.user} />}>
              <Route path="/login" element={<Login login={setAuthData} />} />
              <Route exact path="/register" element={<Register />} />
            </Route>
            <Route element={<PrivateRoute auth={cookies.user} logout={removeAuthData} />}>
              <Route path="/" element={<Chat/>} />
            </Route>
            <Route path='*' element={<PageNotFound />} />
          </Routes>
        </Container>
        <Footer />
      </Router>
    </Container>
  );
}

export default App;