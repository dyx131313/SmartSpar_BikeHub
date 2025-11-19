import path from 'path'
import { defineConfig, loadEnv  } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'

// https://vite.dev/config/
export default ({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  const target = env.VITE_API_BASE || 'http://localhost:5000'

  return defineConfig({
    plugins: [
      tanstackRouter({
        target: 'react',
        autoCodeSplitting: true,
      }),
      react(),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    // 开发时代理 /api 到后端，避免浏览器 CORS
    server: {
      proxy: {
        '/api': {
          target,
          changeOrigin: true,
          secure: false,
          rewrite: (p) => p, // 保留 /api 前缀
        },
      },
    },
  })
}
