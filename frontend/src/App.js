import logo from "./logo.svg";
import "./App.css";
import FaceCam from "./Facecam";
import LiveAudio from "./Liveaudio";

function App() {
  return (
    <>
      <h1>Real-time Face and Speech Recognition</h1>
      <FaceCam />
      <LiveAudio />
    </>
  );
}

export default App;
