// App.jsx

import {
  BrowserRouter as Router,
  Routes,
  Route,
  Outlet,
} from "react-router-dom";

// Layout Components
import ButtonGradient from "./assets/svg/ButtonGradient";
import Benefits from "./components/Benefits";
import Footer from "./components/Footer";
import Header from "./components/Header";
import Hero from "./components/Hero";

// Page Components
import ResumeUploader from "./pages/ResumeUploader";
import Interview from "./pages/Interview";
import Results from "./pages/Results";
import ForgotPassword from "./pages/ForgotPassword";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Signup from "./pages/Signup";
// import Dashboard from "./pages/Dashboard"; // Optional future route

/**
 * Layout wrapper that adds Header and Footer to all nested pages.
 * <Outlet /> renders the matched child component inside this layout.
 */
const Layout = () => {
  return (
    <>
      <Header />
      <Outlet />
      <Footer />
    </>
  );
};

/**
 * Home page layout with top padding and core marketing sections.
 */
const Home = () => {
  return (
    <div className="pt-[4.75rem] lg:pt-[5.25rem] overflow-hidden">
      <Hero />
      <Benefits />
      <ButtonGradient />
    </div>
  );
};

/**
 * Root App Component: Manages routing for all pages in the application.
 */
function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Routes using the common Header + Footer layout */}
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgetpassword" element={<ForgotPassword />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/resumeuploader" element={<ResumeUploader />} />
            <Route path="/interview" element={<Interview />} />
            <Route path="/results" element={<Results />} />
            {/* <Route path="/dashboard" element={<Dashboard />} /> */}
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
