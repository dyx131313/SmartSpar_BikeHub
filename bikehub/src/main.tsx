import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'
import App from './App.tsx'
import './styles/index.css'
import SignIn from './pages/SignIn.tsx'
import SignUp from './pages/SignUp.tsx'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Toaster richColors />
      <Routes>
        <Route path="/" element={<App />} />
        {/* 占位：后续用模板中的登录注册页替换 */}
        <Route path="/sign-in" element={<SignIn />} />
        <Route path="/sign-up" element={<SignUp />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)