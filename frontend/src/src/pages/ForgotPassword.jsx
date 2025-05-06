import { useState } from "react";
import { Link } from "react-router-dom";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    // Implement password reset email logic here
    console.log("Reset link sent to", email);
    setMessage("A password reset link has been sent to your email.");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-lg shadow-md w-96"
      >
        <h2 className="text-3xl font-bold mb-6 text-gray-800 text-center">
          Forgot Password
        </h2>
        <input
          type="email"
          placeholder="Enter your email"
          className="w-full p-3 border border-gray-300 rounded mb-4 focus:outline-none focus:border-blue-600"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <button
          type="submit"
          className="w-full bg-purple-600 text-white py-3 rounded hover:bg-purple-700 transition"
        >
          Send Reset Link
        </button>
        {message && (
          <p className="mt-4 text-center text-green-600">{message}</p>
        )}
        <div className="mt-4 text-center">
          <Link to="/login" className="text-blue-600 hover:underline">
            Back to Login
          </Link>
        </div>
      </form>
    </div>
  );
};

export default ForgotPassword;
