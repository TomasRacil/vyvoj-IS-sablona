import React, { useEffect, useState } from 'react';
import axiosInstance from '../api/axiosInstance';
import { User } from '../types/user';

const ProfilePage: React.FC = () => {
    const [profile, setProfile] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await axiosInstance.get<User>('/users/me');
                setProfile(response.data);
                setLoading(false);
            } catch (err: any) {
                setError(err.response?.data?.message || 'Chyba při načítání profilu');
                setLoading(false);
            }
        };

        fetchProfile();
    }, []);

    if (loading) return <div className="text-center p-10 text-gray-500 italic">Načítání profilu...</div>;
    if (error) return <div className="text-center p-10 text-red-500 font-medium">{error}</div>;
    if (!profile) return null;

    return (
        <div className="max-w-2xl mx-auto bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100 mt-10">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-700 h-32 flex items-end justify-center pb-6">
                <div className="bg-white p-2 rounded-full shadow-lg -mb-16">
                    <div className="bg-gray-200 rounded-full h-24 w-24 flex items-center justify-center text-4xl text-gray-500 font-bold">
                        {profile.username.charAt(0).toUpperCase()}
                    </div>
                </div>
            </div>
            
            <div className="pt-20 pb-12 px-8 text-center">
                <h1 className="text-3xl font-extrabold text-gray-900 mb-1">{profile.username}</h1>
                <p className="text-gray-500 mb-8">{profile.email}</p>
                
                <div className="grid grid-cols-2 gap-4 text-left max-w-md mx-auto mb-10">
                    <div className="bg-gray-50 p-4 rounded-2xl">
                        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Členem od</span>
                        <p className="text-gray-800 font-medium mt-1">
                            {new Date(profile.created_at).toLocaleDateString('cs-CZ')}
                        </p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-2xl">
                        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Uživatelské ID</span>
                        <p className="text-gray-800 font-mono text-xs mt-1 truncate" title={profile.id}>
                            {profile.id}
                        </p>
                    </div>
                </div>

                <div className="text-left max-w-md mx-auto">
                    <h3 className="text-sm font-bold text-gray-900 mb-3 uppercase tracking-widest">Moje Role</h3>
                    <div className="flex flex-wrap gap-2">
                        {profile.roles.length > 0 ? (
                            profile.roles.map(role => (
                                <span key={role.id} className="bg-blue-100 text-blue-700 px-4 py-1.5 rounded-full text-sm font-bold shadow-sm">
                                    {role.name.toUpperCase()}
                                </span>
                            ))
                        ) : (
                            <span className="text-gray-400 italic">Nemáte přiřazeny žádné role.</span>
                        )}
                    </div>
                </div>
            </div>
            
            <div className="bg-gray-50 px-8 py-6 flex justify-between items-center border-t border-gray-100">
                <span className="text-xs text-gray-400">IS Šablona v2.0</span>
                <button className="text-blue-600 hover:text-blue-800 text-sm font-semibold transition-colors">
                    Upravit profil
                </button>
            </div>
        </div>
    );
};

export default ProfilePage;
