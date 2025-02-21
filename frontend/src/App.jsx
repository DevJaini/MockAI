// App.js
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Outlet,
} from "react-router-dom";
import ButtonGradient from "./assets/svg/ButtonGradient";
import Benefits from "./components/Benefits";
import Footer from "./components/Footer";
import Header from "./components/Header";
import Hero from "./components/Hero";
import ResumeUploader from "./pages/ResumeUploader";
import Interview from "./pages/Interview";
// import Results from "./pages/Results";
import ForgotPassword from "./pages/ForgotPassword";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Signup from "./pages/SignUp";
// import Dashboard from "./pages/Dashboard";

const Layout = () => {
  return (
    <>
      <Header />
      {/* The Outlet renders the matched child route */}
      <Outlet />
      <Footer />
    </>
  );
};

const Home = () => {
  return (
    <>
      <div className="pt-[4.75rem] lg:pt-[5.25rem] overflow-hidden">
        <Hero />
        <Benefits />
      </div>

      <ButtonGradient />
    </>
  );
};

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgetpassword" element={<ForgotPassword />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/resumeuploader" element={<ResumeUploader />} />
            <Route path="/interview" element={<Interview />} />
            {/* <Route path="/results" element={<Results />} /> */}
            {/* <Route path="/dashboard" element={<Dashboard />} /> */}
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
