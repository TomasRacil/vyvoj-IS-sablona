import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import UsersPage from './pages/UsersPage';
import { JSX } from 'react';
import AuthPage from './pages/AuthPage';
import ProtectedRoute from './components/ProtectedRoute'; // Import ProtectedRoute
import { useAuth } from './contexts/AuthContext';

function App(): JSX.Element { // Přidán typ návratové hodnoty
  const { isAuthenticated, logout } = useAuth();

  return (
    <Router>
      <div className="flex flex-col min-h-screen min-w-screen bg-gray-100">
        <nav className="bg-blue-600 p-4 shadow-md mb-6">
          <ul className="flex space-x-6 container mx-auto">
            <li><Link to="/" className="hover:text-blue-200 transition-colors">Domů</Link></li>
            {isAuthenticated && ( // Zobrazit pouze pokud je uživatel přihlášen
              <li><Link to="/users" className="hover:text-blue-200 transition-colors">Uživatelé</Link></li>
            )}
            {isAuthenticated ? (
              <li><button onClick={logout} className="hover:text-blue-200 transition-colors">Odhlásit se</button></li>
            ) : (
              <li><Link to="/auth/login" className="hover:text-blue-200 transition-colors">Přihlášení</Link></li>
            )}
          </ul>
        </nav>

        {/* Hlavní obsah */}
        <main className="flex-grow p-6 container mx-auto text-black">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route element={<ProtectedRoute />}>
              <Route path="/users" element={<UsersPage />} />
            </Route>
            <Route path="/auth/login" element={<AuthPage key="login" mode="login" />} />
            <Route path="/auth/register" element={<AuthPage key="register" mode="register" />} />
          </Routes>
        </main>

        {/* Patička (volitelně) */}
        <footer className="text-center p-4 text-gray-500 mt-auto text-sm">
          © {new Date().getFullYear()} IS Šablona
        </footer>
      </div>
    </Router>
  );
}

export default App;