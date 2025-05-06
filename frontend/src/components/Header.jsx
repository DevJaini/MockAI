import { useLocation, useNavigate } from "react-router-dom";
import { disablePageScroll, enablePageScroll } from "scroll-lock";
import { brainwaveSymbol } from "../assets";
import { navigation } from "../constants";
import Button from "./Button";
import MenuSvg from "../assets/svg/MenuSvg";
import { HamburgerMenu } from "./design/Header";
import { useState, useEffect } from "react";

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [openNavigation, setOpenNavigation] = useState(false);
  const [user, setUser] = useState(null); // Track logged-in user

  useEffect(() => {
    // Simulating user authentication (Replace this with real auth logic)
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser)); // Set user if logged in
    }
  }, []);

  const toggleNavigation = () => {
    if (openNavigation) {
      setOpenNavigation(false);
      enablePageScroll();
    } else {
      setOpenNavigation(true);
      disablePageScroll();
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem("user"); // Clear user data
    setUser(null);
    navigate("/");
  };

  return (
    <div
      className={`fixed top-0 left-0 w-full z-50 border-b border-n-6 lg:bg-n-8/90 lg:backdrop-blur-sm ${
        openNavigation ? "bg-n-8" : "bg-n-8/90 backdrop-blur-sm"
      }`}
    >
      <div className="flex items-center justify-between px-5 lg:px-7.5 xl:px-10 max-lg:py-4">
        {/* Left: Logo + Bold Text */}
        <a href="/" className="flex items-center">
          <img
            src={brainwaveSymbol}
            className="w-[40px] h-[40px]"
            alt="Brainwave"
          />
          <span className="ml-2 font-bold text-xl">MockAi</span>
        </a>

        <nav
          className={`${
            openNavigation ? "flex" : "hidden"
          } fixed top-[5rem] left-0 right-0 bottom-0 bg-n-8 lg:static lg:flex lg:mx-auto lg:bg-transparent`}
        >
          <div className="relative z-2 flex flex-col items-center justify-center m-auto lg:flex-row">
            {navigation.map((item) => (
              <a
                key={item.id}
                href={item.url}
                onClick={() => setOpenNavigation(false)}
                className={`block relative font-code text-2xl uppercase text-n-1 transition-colors hover:text-color-1 ${
                  item.onlyMobile ? "lg:hidden" : ""
                } px-6 py-6 md:py-8 lg:-mr-0.25 lg:text-xs lg:font-semibold ${
                  item.url === location.pathname
                    ? "z-2 text-white font-bold lg:text-n-1"
                    : "lg:text-n-1/50"
                } lg:leading-5 lg:hover:text-n-1 xl:px-12`}
              >
                {item.title}
              </a>
            ))}
          </div>

          <HamburgerMenu />
        </nav>

        {/* If user is logged in */}
        {user ? (
          <div className="flex items-center space-x-4">
            <span className="text-white font-semibold">
              Hello, {user.username}
            </span>
            <Button
              className="px-4 py-2 text-white"
              onClick={() => navigate("/profile")}
            >
              Profile
            </Button>
            <Button
              className="px-4 py-2 rounded-lg text-white"
              onClick={handleSignOut}
            >
              Sign Out
            </Button>
          </div>
        ) : (
          <>
            <Button
              onClick={() => navigate("/signup")}
              className={`button hidden mr-8 transition-colors lg:block px-4 py-2 rounded-lg ${
                location.pathname === "/signup"
                  ? "text-white font-bold bg-purple-600"
                  : ""
              }`}
            >
              Sign Up
            </Button>

            <Button
              className={`hidden lg:flex px-4 py-2 rounded-lg ${
                location.pathname === "/login"
                  ? "bg-purple-600 text-white font-bold"
                  : ""
              }`}
              onClick={() => navigate("/login")}
            >
              Log In
            </Button>
          </>
        )}

        <Button
          className="ml-auto lg:hidden"
          px="px-3"
          onClick={toggleNavigation}
        >
          <MenuSvg openNavigation={openNavigation} />
        </Button>
      </div>
    </div>
  );
};

export default Header;
