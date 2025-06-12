import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./styles/main.css";
import { CookiesProvider } from "react-cookie";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <CookiesProvider defaultSetOptions={{ path: "/" }}>
            <App />
        </CookiesProvider>
    </StrictMode>
);
