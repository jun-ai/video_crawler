import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      // Phase 27: 改走本地 uvicorn (:8000) 才能命中新加的 /material/{id}/interpretations/export 路由
      // (线上 api.fluenty.cn 还没部署, 会 404)
      // 本地 uvicorn 的 DATABASE_URL 走 SSH 隧道转发到生产 MySQL, 数据是真实的
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        headers: {
          'Accept-Ranges': 'bytes'
        }
      },
      '/video': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true
      }
    }
  }
})
