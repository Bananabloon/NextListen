import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    strictPort: true,
    port: 5173,
    allowedHosts: ['86d5-92-63-39-59.ngrok-free.app']
  }
})
