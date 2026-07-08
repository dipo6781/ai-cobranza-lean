import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Optimización de build para producción
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          supabase: ['@supabase/supabase-js']
        }
      }
    },
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: false,
    cssCodeSplit: true
  },
  // Optimizaciones del servidor de desarrollo
  server: {
    port: 5173,
    open: true
  },
  // Pre-optimización de dependencias
  optimizeDeps: {
    include: ['react', 'react-dom', '@supabase/supabase-js']
  }
})
