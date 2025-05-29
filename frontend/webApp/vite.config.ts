import { defineConfig } from "vite";
import { DOMAIN } from "./src/config/url.config";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
    return {
        plugins: [react()],
        server: {
            host: "0.0.0.0",
            strictPort: true,
            port: 5173,
            allowedHosts: [DOMAIN],
        },
    };
});
