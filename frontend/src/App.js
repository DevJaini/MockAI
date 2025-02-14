import logo from "./logo.svg";
import "./App.css";

function App() {
  return (
    <div>
      <header>
        <h1>Welcome to My Home Page</h1>
      </header>
      <main>
        <p>This is the content of the home page.</p>
      </main>
      <footer>
        <p>&copy; {new Date().getFullYear()} My Website</p>
      </footer>
    </div>
  );
}

export default App;
