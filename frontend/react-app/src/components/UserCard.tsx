import React, { useState, useEffect } from 'react';
import { User } from '../types/user';

/**
 * Props pro komponentu UserCard.
 */
interface UserCardProps {
    user: User | null | undefined; // Objekt uživatele, může být null nebo undefined
    onDeleteUser?: (userId: string) => void; // Volitelná funkce pro smazání uživatele
    onSaveUser?: (userId: string, updatedData: Partial<Pick<User, 'username' | 'email'>>) => void; // Funkce pro uložení změn
}

/**
 * Komponenta pro zobrazení uživatelských informací ve formě karty.
 * Používá Tailwind CSS pro stylování.
 */
const UserCard: React.FC<UserCardProps> = ({ user, onDeleteUser, onSaveUser }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [editedUserData, setEditedUserData] = useState<Partial<Pick<User, 'username' | 'email'>>>({
        username: '',
        email: '',
    });

    useEffect(() => {
        if (user) {
            setEditedUserData({ username: user.username, email: user.email });
        }
    }, [user]);

    if (!user) {
        return (
            <div className="max-w-sm rounded overflow-hidden shadow-lg bg-white p-6 border border-gray-200">
                <p className="text-gray-700">Informace o uživateli nejsou k dispozici.</p>
            </div>
        );
    }

    const formatDate = (dateString?: string): string => { // Funkce pro formátování data
        if (!dateString) return 'Nezadáno';
        try {
            return new Date(dateString).toLocaleDateString('cs-CZ', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            console.error("Chyba při formátování data:", error);
            return "Neplatné datum";
        }
    };

    const handleDelete = () => {
        if (user && user.id && onDeleteUser) {
            onDeleteUser(user.id); // Zavoláme funkci pro smazání s ID uživatele
        }
    };

    const handleEditClick = () => {
        if (user) {
            setEditedUserData({ username: user.username, email: user.email });
            setIsEditing(true);
        }
    };

    const handleCancelEdit = () => {
        setIsEditing(false);
        if (user) { // Reset na původní hodnoty
            setEditedUserData({ username: user.username, email: user.email });
        }
    };

    const handleSaveEdit = () => {
        if (user && user.id && onSaveUser) {
            onSaveUser(user.id, editedUserData);
        }
        setIsEditing(false);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setEditedUserData(prev => ({ ...prev, [name]: value }));
    };

    return (
        <div className="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl my-4 border border-gray-200">
            <div className="p-8">
                {isEditing ? (
                    <input
                        type="text"
                        name="username"
                        value={editedUserData.username}
                        onChange={handleInputChange}
                        className="uppercase tracking-wide text-sm text-indigo-500 font-semibold border-b-2 border-indigo-500 focus:outline-none w-full mb-1"
                    />
                ) : (
                    <div className="uppercase tracking-wide text-sm text-indigo-500 font-semibold">{user.username}</div>
                )}
                <p className="block mt-1 text-xs leading-tight font-medium text-gray-500">ID: {user.id}</p>
                <div className="mt-4">
                    <div className="mb-2">
                        <p className="text-sm font-semibold text-gray-600">Email:</p>
                        {isEditing ? (
                            <input
                                type="email"
                                name="email"
                                value={editedUserData.email}
                                onChange={handleInputChange}
                                className="text-gray-800 border-b-2 border-gray-300 focus:border-indigo-500 focus:outline-none w-full"
                            />
                        ) : (
                            <a href={`mailto:${user.email}`} className="text-gray-800 hover:text-indigo-600">{user.email}</a>
                        )}
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-gray-600">Datum registrace:</p>
                        <p className="text-gray-800">{formatDate(user.created_at)}</p>
                    </div>
                </div>
                {isEditing ? (
                    <div className="mt-6 space-y-3 sm:space-y-0 sm:flex sm:space-x-3">
                        <button
                            onClick={handleSaveEdit}
                            className="w-full sm:w-auto bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                        >
                            Uložit
                        </button>
                        <button
                            onClick={handleCancelEdit}
                            className="w-full sm:w-auto bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                        >
                            Zrušit
                        </button>
                    </div>
                ) : (
                    <div className="mt-6 space-y-3">
                        {onSaveUser && ( // Tlačítko Editovat se zobrazí, pokud je onSaveUser definováno
                            <div>
                                <button onClick={handleEditClick} className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                                    Editovat uživatele
                                </button>
                            </div>
                        )}
                        {onDeleteUser && (
                            <div>
                                <button onClick={handleDelete} className="w-full bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                                    Smazat uživatele
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default UserCard;