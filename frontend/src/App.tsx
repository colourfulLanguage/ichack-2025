import { Route, Routes } from "react-router-dom";

import IndexPage from "@/pages/index";
import ProcessPage from "@/pages/proccess";
import ResultsPage from "@/pages/results";
import AboutPage from "@/pages/about";
import CheckPage from "./pages/check";
import ConfirmPage from "./pages/confirm";

function App() {
  return (
    <Routes>
      <Route element={<IndexPage />} path="/" />
      <Route element={<ProcessPage />} path="/process" />
      <Route element={<ResultsPage />} path="/results" />
      <Route element={<AboutPage />} path="/about" />
      <Route element={<CheckPage />} path="/check" />
      <Route element={<ConfirmPage />} path="/confirm" />
    </Routes>
  );
}

export default App;
