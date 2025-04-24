import React, { useState, useEffect } from 'react';
import axios from 'axios'; // Budete potřebovat axios
import { User } from '../types/user'; // Definujte si typ User

const UsersPage: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                setLoading(true);
                // Použití relativní cesty díky proxy ve vite.config.js
                const response = await axios.get<User[]>('/api/v1/users');
                setUsers(response.data);
                setError(null);
            } catch (err) {
                console.error("Chyba při načítání uživatelů:", err);
                setError('Nepodařilo se načíst data uživatelů.');
            } finally {
                setLoading(false);
            }
        };

        fetchUsers();
    }, []); // Prázdné pole závislostí znamená, že se efekt spustí jen jednou po mountnutí

    if (loading) return <p className="text-center">Načítám uživatele...</p>;
    if (error) return <p className="text-center text-red-600">{error}</p>;

    return (
        <div>
            <h1 className="text-3xl font-bold mb-4">Seznam Uživatelů</h1>
            {users.length === 0 ? (
                <p>Nenalezeni žádní uživatelé.</p>
            ) : (
                <ul className="list-disc pl-5 space-y-2">
                    {users.map((user) => (
                        <li key={user.id}>
                            {user.username} ({user.email}) - Vytvořen: {new Date(user.created_at).toLocaleDateString()}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default UsersPage;
