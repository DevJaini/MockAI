import React, { useRef, useState, useEffect, useCallback } from "react";
import Webcam from "react-webcam";

const FaceCam = () => {
    const webcamRef = useRef(null);
    const [faceConfidence, setFaceConfidence] = useState(100);
    const [socket, setSocket] = useState(null);

    useEffect(() => {
        let ws;

        const connectWebSocket = () => {
            ws = new WebSocket("ws://127.0.0.1:8000/face-confidence");

            ws.onopen = () => {
                console.log("Connected to FastAPI WebSocket.");
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.face_confidence !== undefined) {
                        setFaceConfidence(data.face_confidence);
                    }
                } catch (error) {
                    console.error("Error parsing WebSocket message:", error);
                }
            };

            ws.onclose = (event) => {
                console.log("WebSocket connection closed.", event);
                setTimeout(connectWebSocket, 2000); // Reconnect after 2 seconds
            };

            ws.onerror = (error) => {
                console.error("WebSocket error:", error);
                ws.close();
            };

            setSocket(ws);
        };

        connectWebSocket();

        return () => {
            ws.close();
        };
    }, []);

    // use useCallback to memoize the captureFrame function
    const captureFrame = useCallback(() => {
        if (webcamRef.current && socket && socket.readyState === WebSocket.OPEN) {
            const imageSrc = webcamRef.current.getScreenshot();
            socket.send(JSON.stringify({ image: imageSrc }));
        }
    }, [socket]);

    useEffect(() => {
        const interval = setInterval(captureFrame, 200);
        return () => clearInterval(interval);
    }, [captureFrame]);

    return (
        <div style={{ textAlign: "center" }}>
            <h2>Face Confidence: {faceConfidence.toFixed(2)}%</h2>
            <Webcam
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                videoConstraints={{ width: 640, height: 480 }}
            />
        </div>
    );
};

export default FaceCam;
