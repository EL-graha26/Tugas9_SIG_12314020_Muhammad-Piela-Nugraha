import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import MapView from './components/MapView'
import { useState } from 'react'

const ProtectedRoute = ({ children }) => {
    const { user } = useAuth()
    return user ? children : <Navigate to="/login" replace />
}


function LoginPage() {
    const { login } = useAuth()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    const navigate = useNavigate() 

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            await login(email, password)
            navigate('/') 
        } catch (err) {
            alert("Login Gagal! Periksa email dan password dari database kamu.")
        }
    }

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#e9e9e9', fontFamily: 'sans-serif' }}>
            <div style={{ padding: '40px 30px', backgroundColor: 'white', borderRadius: '24px', boxShadow: '0 4px 14px rgba(0,0,0,0.05)', width: '320px' }}>
                
                <h2 style={{ textAlign: 'center', color: '#111', marginBottom: '30px', fontSize: '24px', fontWeight: '600' }}>
                    Welcome back
                </h2>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    <input 
                        type="email" 
                        placeholder="Email" 
                        style={{ padding: '14px 16px', borderRadius: '12px', border: '2px solid #e0e0e0', outline: 'none', fontSize: '15px' }} 
                        onChange={e => setEmail(e.target.value)} 
                        required 
                    />
                    <input 
                        type="password" 
                        placeholder="Password" 
                        style={{ padding: '14px 16px', borderRadius: '12px', border: '2px solid #e0e0e0', outline: 'none', fontSize: '15px' }} 
                        onChange={e => setPassword(e.target.value)} 
                        required 
                    />
                    <button 
                        type="submit" 
                        style={{ padding: '14px', backgroundColor: '#E60023', color: 'white', border: 'none', borderRadius: '24px', cursor: 'pointer', fontWeight: 'bold', fontSize: '15px', marginTop: '10px' }}
                    >
                        Log in
                    </button>
                </form>
            </div>
        </div>
    )
}

// Router Utama
function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/" element={
                        <ProtectedRoute>
                            <div style={{ height: '100vh', width: '100%' }}>
                                <MapView />
                            </div>
                        </ProtectedRoute>
                    } />
                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </Router>
        </AuthProvider>
    )
}

export default App