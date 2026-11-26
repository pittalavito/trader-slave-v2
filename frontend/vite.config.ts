import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In sviluppo le chiamate a /api vanno al backend locale, come fa Caddy in produzione.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
