import React, { useState } from 'react';
import { UserCreationData } from '../types/user'; // Můžete si vytvořit tento typ

interface CreateUserPopupProps {
    isOpen: boolean;
    onClose: () => void;
    onCreateUser: (userData: UserCreationData) => Promise<void>; // Funkce pro vytvoření uživatele
}

const CreateUserPopup: React.FC<CreateUserPopupProps> = ({ isOpen, onClose, onCreateUser }) => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsSubmitting(true);

        if (!username || !email || !password) {
            setError('Všechna pole jsou povinná.');
            setIsSubmitting(false);
            return;
        }

        try {
            await onCreateUser({ username, email, password });
            setUsername('');
            setEmail('');
            setPassword('');
            onClose(); // Zavřít popup po úspěšném vytvoření
        } catch (err) {
            setError('Nepodařilo se vytvořit uživatele. Zkuste to prosím znovu.');
            console.error("Chyba při vytváření uživatele:", err);
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!isOpen) {
        return null;
    }

    return (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex justify-center items-center z-50">
            <div className="relative p-8 border w-full max-w-md shadow-lg rounded-md bg-white">
                <button
                    onClick={onClose}
                    className="absolute top-0 right-0 mt-4 mr-4 text-gray-700 hover:text-gray-900"
                    aria-label="Zavřít"
                >
                    &times;
                </button>
                <h2 className="text-2xl font-bold mb-6 text-center">Vytvořit nového uživatele</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                            Uživatelské jméno
                        </label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                            required
                        />
                    </div>
                    <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
                            Email
                        </label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                            required
                        />
                    </div>
                    <div className="mb-6">
                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
                            Heslo
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                            required
                        />
                    </div>
                    {error && <p className="text-red-500 text-xs italic mb-4">{error}</p>}
                    <div className="flex items-center justify-between">
                        <button
                            type="submit"
                            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? 'Vytváření...' : 'Vytvořit'}
                        </button>
                        <button
                            type="button"
                            onClick={onClose}
                            className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                        >
                            Zrušit
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateUserPopup;
