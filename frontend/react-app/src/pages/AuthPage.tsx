import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axiosInstance from '../api/axiosInstance';

interface AuthPageProps {
    mode: 'login' | 'register';
}

const AuthPage: React.FC<AuthPageProps> = ({ mode }) => {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const navigate = useNavigate();
    const { login } = useAuth();

    const isRegisterMode = mode === 'register';

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            let response;
            if (isRegisterMode) {
                // Endpoint pro registraci
                response = await axiosInstance.post('/auth/register', {
                    username: username,
                    email: email,
                    password: password,
                });

                const accessToken = response.data.access_token;
                const refreshToken = response.data.refresh_token;

                login({ accessToken, refreshToken });
                console.log('Registrace a přihlášení úspěšné, tokeny uloženy do kontextu.');
                alert('Registrace úspěšná! Jste přihlášeni. Tokeny v konzoli.');
                navigate('/'); // Přesměrování na domovskou stránku
            } else {
                // Endpoint pro přihlášení
                response = await axiosInstance.post('/auth/login', {
                    username_or_email: email, // Backend očekává username_or_email
                    password: password,
                });

                const accessToken = response.data.access_token;
                const refreshToken = response.data.refresh_token;

                login({ accessToken, refreshToken });
                console.log('Přihlášení úspěšné, tokeny uloženy do kontextu.');
                navigate('/');
            }

        } catch (err) {
            const actionText = isRegisterMode ? "registraci" : "přihlašování";
            console.error(`Chyba při ${actionText}:`, err);
            if (axios.isAxiosError(err) && err.response) {
                setError(err.response.data.message || `Nepodařilo se provést ${actionText}. Zkontrolujte údaje.`);
            } else {
                setError('Došlo k neočekávané chybě.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-full px-6 py-12 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-sm">
                <h2 className="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
                    {isRegisterMode ? 'Vytvořte si nový účet' : 'Přihlaste se k vašemu účtu'}
                </h2>
            </div>

            <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
                <form className="space-y-6" onSubmit={handleSubmit}>
                    {isRegisterMode && (
                        <div>
                            <label htmlFor="username" className="block text-sm font-medium leading-6 text-gray-900">
                                Uživatelské jméno
                            </label>
                            <div className="mt-2">
                                <input
                                    id="username"
                                    name="username"
                                    type="text"
                                    autoComplete="username"
                                    required
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 px-2"
                                />
                            </div>
                        </div>
                    )}
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium leading-6 text-gray-900">
                            {isRegisterMode ? 'Emailová adresa' : 'Emailová adresa nebo uživatelské jméno'}
                        </label>
                        <div className="mt-2">
                            <input
                                id="email"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 px-2"
                            />
                        </div>
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium leading-6 text-gray-900">Heslo</label>
                        <div className="mt-2">
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="current-password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 px-2"
                            />
                        </div>
                    </div>
                    {error && <p className="text-sm text-red-600">{error}</p>}
                    <div>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50"
                        >
                            {isLoading
                                ? (isRegisterMode ? 'Registrace...' : 'Přihlašování...')
                                : (isRegisterMode ? 'Zaregistrovat se' : 'Přihlásit se')}
                        </button>
                    </div>
                </form>

                <p className="mt-10 text-center text-sm text-gray-500">
                    {isRegisterMode ? (
                        <>
                            Máte již účet?{' '}
                            <Link to="/auth/login" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">Přihlaste se</Link>
                        </>
                    ) : (
                        <>
                            Nemáte účet?{' '}
                            <Link to="/auth/register" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">Zaregistrujte se</Link>
                        </>
                    )}
                </p>
            </div>
        </div>
    );
};

export default AuthPage;