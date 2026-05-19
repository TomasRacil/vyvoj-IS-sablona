import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import UsersPage from './pages/UsersPage';
import { JSX } from 'react';
import AuthPage from './pages/AuthPage';
import BooksPage from './pages/BooksPage';
import BookDetailPage from './pages/BookDetailPage';
import BookEditPage from './pages/BookEditPage';
import ProfilePage from './pages/ProfilePage';
import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './contexts/AuthContext';

function App(): JSX.Element {
  const { isAuthenticated, logout, userRoles } = useAuth();

  return (
    <Router>
      <div className="flex flex-col min-h-screen min-w-screen bg-gray-100">
        <nav className="bg-blue-600 p-4 shadow-md mb-6">
          <ul className="flex space-x-6 container mx-auto text-white">
            <li><Link to="/" className="hover:text-blue-200 transition-colors font-medium">Domů</Link></li>
            <li><Link to="/books" className="hover:text-blue-200 transition-colors font-medium">Knihy</Link></li>
            {userRoles.includes('admin') && (
              <li><Link to="/users" className="hover:text-blue-200 transition-colors font-medium">Uživatelé</Link></li>
            )}
            {isAuthenticated && (
              <li><Link to="/profile" className="hover:text-blue-200 transition-colors font-medium">Můj Profil</Link></li>
            )}
            {isAuthenticated ? (
              <li><button onClick={logout} className="hover:text-blue-200 transition-colors font-medium">Odhlásit se</button></li>
            ) : (
              <li><Link to="/auth/login" className="hover:text-blue-200 transition-colors font-medium">Přihlášení</Link></li>
            )}
          </ul>
        </nav>

        {/* Hlavní obsah */}
        <main className="flex-grow p-6 container mx-auto text-black">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/books" element={<BooksPage />} />
            <Route path="/books/:id" element={<BookDetailPage />} />
            <Route element={<ProtectedRoute />}>
              <Route path="/profile" element={<ProfilePage />} />
            </Route>
            <Route element={<ProtectedRoute allowedRoles={['admin', 'editor']} />}>
              <Route path="/books/:id/edit" element={<BookEditPage />} />
            </Route>
            <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
              <Route path="/users" element={<UsersPage />} />
            </Route>
            <Route path="/auth/login" element={<AuthPage key="login" mode="login" />} />
            <Route path="/auth/register" element={<AuthPage key="register" mode="register" />} />
          </Routes>
        </main>

        {/* Patička */}
        <footer className="text-center p-4 text-gray-500 mt-auto text-sm">
          © {new Date().getFullYear()} IS Šablona
        </footer>
      </div>
    </Router>
  );
}

export default App;