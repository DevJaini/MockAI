import { useState, useEffect } from "react";
import { heroBackground } from "../assets";
import Section from "../components/Section";
import { Rings } from "../components/design/Hero";
import { useNavigate } from "react-router-dom";

const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState({ username: "", email: "" });
  const [showModal, setShowModal] = useState(false);
  const [passwords, setPasswords] = useState({
    oldPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem("user"));
    if (storedUser) {
      setUser(storedUser);
    } else {
      navigate("/login"); // Redirect to login if user is not authenticated
    }
  }, [navigate]);

  const handleUpdateProfile = (e) => {
    e.preventDefault();
    localStorage.setItem("user", JSON.stringify(user));
    alert("Profile updated successfully!");
  };

  const handleResetPassword = (e) => {
    e.preventDefault();

    if (passwords.newPassword !== passwords.confirmPassword) {
      alert("New password and confirm password do not match!");
      return;
    }

    console.log("Old Password:", passwords.oldPassword);
    console.log("New Password:", passwords.newPassword);

    // Reset passwords after submission (For now, just clear the fields)
    setPasswords({ oldPassword: "", newPassword: "", confirmPassword: "" });
    setShowModal(false);
    alert("Password updated successfully!");
  };

  return (
    <Section className="relative min-h-screen flex flex-col items-center justify-center p-6 text-center">
      {/* Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute -top-[50%] left-1/2 w-[200%] -translate-x-1/2 
                        md:-top-[40%] md:w-[130%] lg:-top-[80%]"
        >
          <img
            src={heroBackground}
            alt="hero background"
            className="w-full object-cover blur-lg"
            width={1440}
            height={1800}
          />
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 bg-white bg-opacity-10 backdrop-blur-lg shadow-xl rounded-xl p-8 max-w-lg w-full">
        <h2 className="text-4xl font-extrabold text-white mb-6">Profile</h2>

        <form onSubmit={handleUpdateProfile} className="flex flex-col gap-4">
          <div className="text-left">
            <label className="block text-white font-semibold mb-1">
              Username:
            </label>
            <input
              type="text"
              value={user.username}
              onChange={(e) => setUser({ ...user, username: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-900"
              required
            />
          </div>

          <div className="text-left">
            <label className="block text-white font-semibold mb-1">
              Email:
            </label>
            <input
              type="email"
              value={user.email}
              onChange={(e) => setUser({ ...user, email: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-900"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full px-6 py-3 bg-purple-500 text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition transform hover:scale-105 mt-2"
          >
            Update Profile
          </button>
        </form>

        <button
          onClick={() => setShowModal(true)}
          className="w-full mt-4 px-6 py-3 border border-white text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition transform mt-10"
        >
          Reset Password
        </button>
      </div>

      <Rings />

      {/* Password Reset Modal */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Reset Password
            </h2>

            <form
              onSubmit={handleResetPassword}
              className="flex flex-col gap-4"
            >
              <input
                type="password"
                placeholder="Old Password"
                value={passwords.oldPassword}
                onChange={(e) =>
                  setPasswords({ ...passwords, oldPassword: e.target.value })
                }
                className="w-full p-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-900"
                required
              />

              <input
                type="password"
                placeholder="New Password"
                value={passwords.newPassword}
                onChange={(e) =>
                  setPasswords({ ...passwords, newPassword: e.target.value })
                }
                className="w-full p-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-900"
                required
              />

              <input
                type="password"
                placeholder="Confirm New Password"
                value={passwords.confirmPassword}
                onChange={(e) =>
                  setPasswords({
                    ...passwords,
                    confirmPassword: e.target.value,
                  })
                }
                className="w-full p-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-900"
                required
              />

              <div className="flex justify-between mt-4">
                <button
                  type="submit"
                  className="px-6 py-2 bg-purple-500 text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition transform hover:scale-105"
                >
                  Submit
                </button>
                <button
                  onClick={() => setShowModal(false)}
                  className="px-6 py-2 bg-purple-500 text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition transform hover:scale-105"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Section>
  );
};

export default Profile;
