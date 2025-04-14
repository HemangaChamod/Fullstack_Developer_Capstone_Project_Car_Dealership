import LoginPanel from "./components/Login/Login";
import { Routes, Route } from "react-router-dom";
import Register from "./components/Register/Register";


function App() {
  return (
    <Routes>
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<LoginPanel />} />
    </Routes>
  );
}
export default App;
