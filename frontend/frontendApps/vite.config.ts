import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '', '');
  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      strictPort: true,
      port: 5173,
      allowedHosts: [env.VITE_NGROK_URL.replace('https://', '').replace('http://', '')]
    }
  }
})