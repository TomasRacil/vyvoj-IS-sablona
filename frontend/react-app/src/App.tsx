import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import UsersPage from './pages/UsersPage';
import { JSX } from 'react';

function App(): JSX.Element { // Přidán typ návratové hodnoty
  return (
    <Router>
      <div className="flex flex-col min-h-screen min-w-screen bg-gray-100">
        {/* Jednoduchá Navigace */}
        <nav className="bg-blue-600 text-white p-4 shadow-md mb-6">
          <ul className="flex space-x-6 container mx-auto">
            <li><Link to="/" className="hover:text-blue-200 transition-colors">Domů</Link></li>
            <li><Link to="/users" className="hover:text-blue-200 transition-colors">Uživatelé</Link></li>
            {/* Přidejte další odkazy */}
          </ul>
        </nav>

        {/* Hlavní obsah */}
        <main className="flex-grow p-6 container mx-auto">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/users" element={<UsersPage />} />
            {/* Přidejte další routy */}
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