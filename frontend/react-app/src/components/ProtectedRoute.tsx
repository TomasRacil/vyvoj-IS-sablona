import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
    allowedRoles?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles }) => {
    const { isAuthenticated, isLoading, userRoles } = useAuth();

    if (isLoading) {
        return <div className="text-center p-10 text-gray-500">Ověřování oprávnění...</div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/auth/login" replace />;
    }

    if (allowedRoles && !allowedRoles.some(role => userRoles.includes(role))) {
        // Pokud má uživatel roli ADMIN, pustíme ho všude (volitelné)
        if (userRoles.includes('admin')) {
            return <Outlet />;
        }
        return (
            <div className="text-center p-10">
                <h1 className="text-2xl font-bold text-red-600">Přístup odepřen</h1>
                <p className="text-gray-600 mt-2">Nemáte dostatečná oprávnění pro přístup k této stránce.</p>
            </div>
        );
    }

    return <Outlet />;
};

export default ProtectedRoute;