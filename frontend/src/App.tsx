import { Route, Routes } from "react-router-dom";

import IndexPage from "@/pages/index";
import ProcessPage from "@/pages/proccess";
import ResultsPage from "@/pages/results";
import AboutPage from "@/pages/about";

function App() {
  return (
    <Routes>
      <Route element={<IndexPage />} path="/" />
      <Route element={<ProcessPage />} path="/process" />
      <Route element={<ResultsPage />} path="/results" />
      <Route element={<AboutPage />} path="/about" />
    </Routes>
  );
}

export default App;
