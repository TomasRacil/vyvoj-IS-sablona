import React, { useState, useEffect } from 'react';
import { User, Role } from '../types/user';
import axiosInstance from '../api/axiosInstance';

interface UserCardProps {
    user: User | null | undefined;
    onDeleteUser?: (userId: string) => void;
    onSaveUser?: (userId: string, updatedData: Partial<Pick<User, 'username' | 'email'>>) => void;
    onUpdateUser?: (updatedUser: User) => void;
}

const UserCard: React.FC<UserCardProps> = ({ user, onDeleteUser, onSaveUser, onUpdateUser }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [editedUserData, setEditedUserData] = useState<Partial<Pick<User, 'username' | 'email'>>>({
        username: '',
        email: '',
    });
    const [availableRoles, setAvailableRoles] = useState<Role[]>([]);
    const [isLoadingRoles, setIsLoadingRoles] = useState(false);

    useEffect(() => {
        if (user) {
            setEditedUserData({ username: user.username, email: user.email });
        }
    }, [user]);

    const fetchAvailableRoles = async () => {
        try {
            setIsLoadingRoles(true);
            const response = await axiosInstance.get<Role[]>('/auth/roles');
            setAvailableRoles(response.data);
        } catch (err) {
            console.error("Chyba při načítání dostupných rolí:", err);
        } finally {
            setIsLoadingRoles(false);
        }
    };

    const handleAddRole = async (roleId: string) => {
        if (!user) return;
        try {
            const response = await axiosInstance.post<User>(`/auth/${user.id}/roles`, { role_id: roleId });
            if (onUpdateUser) {
                onUpdateUser(response.data);
            }
            setAvailableRoles([]); // Zavřít výběr
        } catch (err) {
            console.error("Chyba při přidávání role:", err);
            alert("Nepodařilo se přidat roli.");
        }
    };

    const handleRemoveRole = async (roleId: string) => {
        if (!user) return;
        try {
            await axiosInstance.delete(`/auth/${user.id}/roles/${roleId}`);
            // Po smazání načteme čerstvá data uživatele
            const response = await axiosInstance.get<User>(`/users/${user.id}`);
            if (onUpdateUser) {
                onUpdateUser(response.data);
            }
        } catch (err) {
            console.error("Chyba při odebírání role:", err);
            alert("Nepodařilo se odebrat roli.");
        }
    };

    if (!user) return null;

    const formatDate = (dateString?: string): string => {
        if (!dateString) return 'Nezadáno';
        return new Date(dateString).toLocaleDateString('cs-CZ');
    };

    return (
        <div className="max-w-md mx-auto bg-white rounded-3xl shadow-xl overflow-hidden md:max-w-2xl my-6 border border-gray-100">
            <div className="p-8">
                <div className="flex justify-between items-start">
                    <div>
                        {isEditing ? (
                            <input
                                type="text"
                                name="username"
                                value={editedUserData.username}
                                onChange={(e) => setEditedUserData({ ...editedUserData, username: e.target.value })}
                                className="text-2xl font-bold text-gray-900 border-b-2 border-blue-500 focus:outline-none"
                            />
                        ) : (
                            <h2 className="text-2xl font-bold text-gray-900">{user.username}</h2>
                        )}
                        <p className="text-xs text-gray-400 mt-1 font-mono">{user.id}</p>
                    </div>
                    <div className="flex space-x-2">
                        {isEditing ? (
                            <>
                                <button onClick={() => { onSaveUser?.(user.id, editedUserData); setIsEditing(false); }} className="bg-green-100 text-green-700 p-2 rounded-full hover:bg-green-200 transition-colors">
                                    ✓
                                </button>
                                <button onClick={() => setIsEditing(false)} className="bg-gray-100 text-gray-700 p-2 rounded-full hover:bg-gray-200 transition-colors">
                                    ✕
                                </button>
                            </>
                        ) : (
                            <button onClick={() => setIsEditing(true)} className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                                Upravit
                            </button>
                        )}
                    </div>
                </div>

                <div className="mt-6 space-y-4">
                    <div>
                        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Email</span>
                        {isEditing ? (
                            <input
                                type="email"
                                name="email"
                                value={editedUserData.email}
                                onChange={(e) => setEditedUserData({ ...editedUserData, email: e.target.value })}
                                className="block w-full text-gray-800 border-b border-gray-200 focus:border-blue-500 focus:outline-none py-1"
                            />
                        ) : (
                            <p className="text-gray-800 font-medium">{user.email}</p>
                        )}
                    </div>

                    <div>
                        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Role</span>
                        <div className="flex flex-wrap gap-2 mt-2">
                            {user.roles.map(role => (
                                <span key={role.id} className="inline-flex items-center bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-bold border border-blue-100">
                                    {role.name.toUpperCase()}
                                    <button onClick={() => handleRemoveRole(role.id)} className="ml-2 text-blue-400 hover:text-red-500 transition-colors">
                                        ✕
                                    </button>
                                </span>
                            ))}
                            <button 
                                onClick={() => { if (availableRoles.length === 0) fetchAvailableRoles(); }}
                                className="inline-flex items-center bg-gray-50 text-gray-400 hover:text-blue-600 px-3 py-1 rounded-full text-xs font-bold border border-gray-200 transition-colors"
                            >
                                + Přidat roli
                            </button>
                        </div>
                        
                        {availableRoles.length > 0 && (
                            <div className="mt-3 p-3 bg-gray-50 rounded-xl border border-gray-100 animate-in fade-in slide-in-from-top-2">
                                <p className="text-[10px] font-bold text-gray-400 uppercase mb-2">Dostupné role:</p>
                                <div className="flex flex-wrap gap-2">
                                    {availableRoles.filter(ar => !user.roles.find(ur => ur.id === ar.id)).map(role => (
                                        <button 
                                            key={role.id}
                                            onClick={() => handleAddRole(role.id)}
                                            className="bg-white hover:bg-blue-600 hover:text-white text-gray-600 px-3 py-1 rounded-lg text-xs font-medium border border-gray-200 shadow-sm transition-all"
                                        >
                                            {role.name}
                                        </button>
                                    ))}
                                    <button onClick={() => setAvailableRoles([])} className="text-[10px] text-gray-400 hover:underline ml-auto">Zavřít</button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <div className="mt-8 pt-6 border-t border-gray-50 flex justify-between items-center">
                    <span className="text-xs text-gray-400 italic">Registrace: {formatDate(user.created_at)}</span>
                    <button 
                        onClick={() => onDeleteUser?.(user.id)}
                        className="text-red-500 hover:text-red-700 text-xs font-bold uppercase tracking-widest transition-colors"
                    >
                        Smazat uživatele
                    </button>
                </div>
            </div>
        </div>
    );
};

export default UserCard;