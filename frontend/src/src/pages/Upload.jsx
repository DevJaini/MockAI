// src/pages/Upload.jsx
import { useState } from "react";
import { useDropzone } from "react-dropzone";
import { useNavigate } from "react-router-dom";

const Upload = () => {
  const [files, setFiles] = useState([]);
  const navigate = useNavigate();

  const { getRootProps, getInputProps } = useDropzone({
    accept: ".pdf,.docx",
    onDrop: (acceptedFiles) => setFiles(acceptedFiles),
  });

  const handleSubmit = () => {
    console.log("Files uploaded:", files);
    navigate("/interview");
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div
        {...getRootProps()}
        className="w-80 h-40 border-2 border-dashed rounded-lg p-4 flex items-center justify-center cursor-pointer hover:border-blue-600 transition"
      >
        <input {...getInputProps()} />
        <p className="text-gray-600">
          Drag & drop your resume or click to select a file
        </p>
      </div>
      {files.length > 0 && (
        <p className="mt-2 text-gray-700">{files[0].name}</p>
      )}
      <button
        className="mt-4 bg-purple-600 text-white px-6 py-2 rounded hover:bg-purple-700 transition"
        onClick={handleSubmit}
      >
        Next
      </button>
    </div>
  );
};

export default Upload;
