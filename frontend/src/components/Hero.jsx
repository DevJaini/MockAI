import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { curve, heroBackground, robot1 } from "../assets";
import Button from "./Button";
import Section from "./Section";
import { BackgroundCircles, BottomLine } from "./design/Hero";
import Generating from "./Generating";

const Hero = () => {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const parallaxRef = useRef(null);

  useEffect(() => {
    if (showModal) {
      document.body.style.overflow = "hidden"; // Prevent scrolling when modal is open
    } else {
      document.body.style.overflow = "auto";
    }
  }, [showModal]);

  const handleGetStarted = () => {
    const user = localStorage.getItem("user");
    if (user) {
      navigate("/resumeuploader");
    } else {
      setShowModal(true);
    }
  };

  return (
    <Section
      className="pt-[12rem] -mt-[5.25rem]"
      crosses
      crossesOffset="lg:translate-y-[5.25rem]"
      customPaddings
      id="hero"
    >
      <div className="container relative" ref={parallaxRef}>
        <div className="relative z-1 max-w-[62rem] mx-auto text-center mb-[3.875rem] md:mb-20 lg:mb-[4rem]">
          <h1 className="h1 mb-6">
            Prepare, Practice, and Perform Your Interview with
            <span className="inline-block relative">
              MockAI
              <img
                src={curve}
                className="absolute top-full left-0 w-full xl:-mt-2"
                width={624}
                height={28}
                alt="Curve"
              />
            </span>
          </h1>
          <p className="body-1 max-w-3xl mx-auto mb-6 text-n-2 lg:mb-8">
            Join <span className="text-purple-400 font-semibold">MockAI</span>{" "}
            and take your job interview preparation to the next level! Upload
            your resume, get AI-powered interview questions tailored to your
            profile, receive real-time feedback on speech and body language, and
            improve your chances of landing your dream job.
          </p>

          <Button onClick={handleGetStarted} white className="ml-2">
            Get started
          </Button>
        </div>

        <div className="relative max-w-[23rem] mx-auto md:max-w-5xl xl:mb-24">
          <div className="relative z-1 p-0.5 rounded-2xl bg-conic-gradient">
            <div className="h-[1rem] rounded-t-[0.9rem]" />
            <div className="aspect-[33/40] rounded-b-[0.9rem] overflow-hidden md:aspect-[688/490] lg:aspect-[1024/490]">
              <img
                src={robot1}
                className="w-full scale-[1.3] translate-y-[2%] md:scale-[1] md:-translate-y-[2%] lg:-translate-y-[15%]"
                alt="AI"
              />
              <Generating className="absolute left-4 right-4 bottom-5 md:left-1/2 md:right-auto md:bottom-8 md:-translate-x-1/2" />
            </div>
          </div>
          <div className="absolute -top-[54%] left-1/2 w-[234%] -translate-x-1/2 md:-top-[46%] md:w-[138%] lg:-top-[104%]">
            <img
              src={heroBackground}
              className="w-full"
              width={1440}
              height={1800}
              alt="hero"
            />
          </div>
          <BackgroundCircles />
        </div>
      </div>

      <BottomLine />

      {/* Modal for login/signup */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-md z-50">
          <div className="bg-white p-6 rounded-xl shadow-lg text-center w-[90%] max-w-sm animate-fadeIn">
            <h2 className="text-xl font-bold mb-4 text-gray-800">
              You need to log in!
            </h2>
            <p className="mb-4 text-gray-600">
              Sign in or create an account to get started.
            </p>
            <div className="flex justify-center gap-4">
              <Button
                onClick={() => navigate("/login")}
                className="text-black px-4 py-2 rounded-lg transition"
              >
                Log In
              </Button>
              <Button
                onClick={() => navigate("/signup")}
                className="text-black px-4 py-2 rounded-lg transition"
              >
                Sign Up
              </Button>
            </div>
            <button
              onClick={() => setShowModal(false)}
              className="mt-4 text-gray-500 hover:text-gray-700"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </Section>
  );
};

export default Hero;
