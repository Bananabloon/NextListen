const mode = import.meta.env?.MODE ?? "development";

const DOMAIN_CONFIG = {
    production: window?.location?.hostname,
    development: import.meta.env.VITE_NGROK_DEVELOPMENT_URL.replace(/https?:\/\//, ""),
};

export const DOMAIN = DOMAIN_CONFIG[mode] || DOMAIN_CONFIG.development;

export const API_URL = `https://${DOMAIN}/api`;

export default {
    DOMAIN,
    API_URL,
};
