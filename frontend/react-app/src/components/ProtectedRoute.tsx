import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute: React.FC = () => {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        // Můžete zobrazit načítací spinner nebo prázdnou stránku, dokud se neověří stav
        return <div>Načítání...</div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/auth/login" replace />;
    }

    return <Outlet />; // Nebo můžete předat `children` prop: return <>{children}</>;
};

export default ProtectedRoute;