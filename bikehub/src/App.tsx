import { useNavigate } from 'react-router-dom'
import './App.css'

function App() {
  const navigate = useNavigate()

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* 顶部 Logo 占位：请将项目 logo.png 放在 public/ 目录下 */}
      <header
        style={{
          padding: '24px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid #eee',
        }}
      >
        <img
          src="/logo.png"
          alt="项目 Logo"
          style={{ height: 56, objectFit: 'contain' }}
          onError={(e) => {
            // 没有提供 logo.png 时的降级占位
            const target = e.currentTarget as HTMLImageElement
            target.style.display = 'none'
          }}
        />
      </header>

      {/* 中间项目名称 */}
      <main
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 16px',
          textAlign: 'center',
        }}
      >
        <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 16 }}>
          SmartSpar BikeHub — 智能共享单车调度
        </h1>
        <p style={{ color: '#666', marginBottom: 32 }}>
          高效预测 · 智能调度 · 便捷骑行
        </p>

        {/* 登录 / 注册按钮 */}
        <div style={{ display: 'flex', gap: 12 }}>
          <button
            onClick={() => navigate('/sign-in')}
            style={{
              padding: '10px 20px',
              borderRadius: 8,
              border: '1px solid #1e40af',
              background: '#1d4ed8',
              color: '#fff',
              fontWeight: 600,
            }}
          >
            登录
          </button>
          <button
            onClick={() => navigate('/sign-up')}
            style={{
              padding: '10px 20px',
              borderRadius: 8,
              border: '1px solid #cbd5e1',
              background: '#fff',
              color: '#0f172a',
              fontWeight: 600,
            }}
          >
            注册
          </button>
        </div>
      </main>

      <footer style={{ textAlign: 'center', padding: 16, color: '#94a3b8' }}>
        © {new Date().getFullYear()} SmartSpar BikeHub
      </footer>
    </div>
  )
}

export default App