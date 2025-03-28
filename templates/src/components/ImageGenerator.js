import React, { useState } from "react";
import axios from "axios";

const ImageGenerator = () => {
  const [prompt, setPrompt] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generateImage = async () => {
    if (!prompt) {
      setError("Please enter a prompt.");
      return;
    }
    setError("");
    setLoading(true);

    try {
      const response = await axios.post(
        "http://localhost:5000/generate", // Backend API endpoint
        { prompt }
      );

      setImageUrl(response.data.image_url);
    } catch (err) {
      setError("Failed to generate image. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl bg-white rounded-lg shadow-xl p-6">
      <h1 className="text-2xl font-bold mb-4 text-center text-gray-700">
        Text-to-Image Generator
      </h1>
      <textarea
        className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        rows="4"
        placeholder="Enter a creative prompt..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <button
        onClick={generateImage}
        className="mt-4 w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 transition duration-300"
        disabled={loading}
      >
        {loading ? "Generating..." : "Generate Image"}
      </button>

      {error && <p className="text-red-500 mt-2 text-center">{error}</p>}

      {imageUrl && (
        <div className="mt-6 text-center">
          <h2 className="text-lg font-semibold mb-2">Generated Image:</h2>
          <img
            src={imageUrl}
            alt="Generated"
            className="w-full rounded-lg shadow-md"
          />
        </div>
      )}
    </div>
  );
};

export default ImageGenerator;