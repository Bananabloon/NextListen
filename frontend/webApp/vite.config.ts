import { defineConfig, loadEnv } from "vite";
import { DOMAIN } from "./src/config/url.config";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, "", "");

    return {
        plugins: [react()],
        server: {
            host: "0.0.0.0",
            strictPort: true,
            port: 5173,
            allowedHosts: [env.VITE_NGROK_DEVELOPMENT_URL.replace(/https?:\/\//, "")],
        },
        resolve: { alias: { "@tabler/icons-react": "@tabler/icons-react/dist/esm/icons/index.mjs" } },
    };
});
