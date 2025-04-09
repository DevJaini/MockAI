import { useState, useEffect } from "react";

const Profile = () => {
  // Dummy profile data; replace with API call to fetch real user data.
  const [user, setUser] = useState({
    name: "Jane Doe",
    email: "jane.doe@example.com",
    bio: "Aspiring professional honing interview skills with AI.",
  });

  useEffect(() => {
    // Fetch user data here if necessary.
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-6">
          Your Profile
        </h2>
        <div className="mb-4">
          <label className="block text-gray-700 font-semibold">Name</label>
          <p className="mt-1 text-gray-600">{user.name}</p>
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 font-semibold">Email</label>
          <p className="mt-1 text-gray-600">{user.email}</p>
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 font-semibold">Bio</label>
          <p className="mt-1 text-gray-600">{user.bio}</p>
        </div>
        {/* You can add an edit profile button and functionality later */}
        <button className="w-full bg-purple-600 text-white py-3 rounded hover:bg-purple-700 transition">
          Edit Profile
        </button>
      </div>
    </div>
  );
};

export default Profile;
