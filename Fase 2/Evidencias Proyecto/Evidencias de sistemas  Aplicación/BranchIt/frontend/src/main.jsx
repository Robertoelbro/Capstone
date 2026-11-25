import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
import "./garden.css";
import "./accessibility.css";
import { BrowserRouter } from "react-router-dom";
import SessionProvider from "./SessionProvider";
import { Analytics } from "@vercel/analytics/react";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <SessionProvider>
        <App />
      </SessionProvider>
      <Analytics />
    </BrowserRouter>
  </React.StrictMode>,
);
