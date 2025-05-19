import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import CallbackPage from "./pages/CallbackPage";
import HomePage from "./pages/HomePage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/callback" element={<CallbackPage />} />
      </Routes>
    </Router>
  );
}

export default App;
