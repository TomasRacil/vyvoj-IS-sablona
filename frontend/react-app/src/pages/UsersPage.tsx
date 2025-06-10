import React, { useState, useEffect } from 'react';
import axios from 'axios'; // Budete potřebovat axios
import { User, UserCreationData } from '../types/user'; // Definujte si typ User
import UserCard from '../components/UserCard';
import CreateUserPopup from '../components/CreateUserPopup';
import axiosInstance from '../api/axiosInstance';

const UsersPage: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [isCreatePopupOpen, setIsCreatePopupOpen] = useState<boolean>(false);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            // Použití relativní cesty díky proxy ve vite.config.js
            const response = await axiosInstance.get<User[]>('/users/');
            setUsers(response.data);
            setError(null);
        } catch (err) {
            console.error("Chyba při načítání uživatelů:", err);
            setError('Nepodařilo se načíst data uživatelů.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []); // Prázdné pole závislostí znamená, že se efekt spustí jen jednou po mountnutí

    const handleOpenCreatePopup = () => setIsCreatePopupOpen(true);
    const handleCloseCreatePopup = () => setIsCreatePopupOpen(false);

    const handleCreateUser = async (userData: UserCreationData) => {
        try {
            // Zde můžete přidat setLoading(true) nebo nějaký indikátor pro popup
            const response = await axiosInstance.post<User>('/auth/register', userData);
            console.log("Uživatel úspěšně vytvořen:", response.data);
            setUsers([...users, response.data]);
        } catch (err) {
            console.error("Chyba při vytváření uživatele:", err);
            setError('Nepodařilo se vytvořit nového uživatele.'); // Můžete zobrazit chybu i v popupu
            throw err; // Předat chybu dál, aby ji mohl zpracovat popup
        }
    };

    const handleRemoveUser = (id: string) => {
        const response = axios.delete('/api/v1/users/' + id, {
        })
        response.then(function (response) {
            console.log(response);
            setUsers(users.filter(user => user.id !== id));
        })
            .catch(function (error) {
                console.log(error);
            })
    }

    const handleSaveUser = async (userId: string, updatedData: Partial<Pick<User, 'username' | 'email'>>) => {
        try {
            const response = await axiosInstance.put<User>(`/users/${userId}`, updatedData);
            setUsers(prevUsers =>
                prevUsers.map(user =>
                    user.id === userId ? { ...user, ...response.data } : user
                )
            );
            console.log("Uživatel úspěšně aktualizován:", response.data);
        } catch (err) {
            console.error(`Chyba při aktualizaci uživatele s ID ${userId}:`, err);
            setError(`Nepodařilo se aktualizovat uživatele ${updatedData.username || userId}.`);
        }
    };
    // if (loading) return <p className="text-center">Načítám uživatele...</p>;
    // if (error) return <p className="text-center text-red-600">{error}</p>;

    return (

        <div>
            {loading && <p className="text-center">Načítám uživatele...</p>}
            {error && <p className="text-center text-red-600">{error}</p>}
            {!loading && !error && (
                <>
                    <div className="mb-6 text-center">
                        <button
                            onClick={handleOpenCreatePopup}
                            className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                        >Vytvořit nového uživatele</button>
                    </div>
                    <h1 className="text-3xl font-bold mb-6 text-center">Seznam Uživatelů</h1>
                    {users.length === 0 ? (
                        <p className="text-center text-gray-500">Nenalezeni žádní uživatelé.</p>
                    ) : (
                        users.map((user) => <UserCard key={user.id} user={user} onDeleteUser={handleRemoveUser} onSaveUser={handleSaveUser} />)
                    )}
                </>
            )}
            <CreateUserPopup
                isOpen={isCreatePopupOpen}
                onClose={handleCloseCreatePopup}
                onCreateUser={handleCreateUser}
            />
        </div>
    );
};

export default UsersPage;
