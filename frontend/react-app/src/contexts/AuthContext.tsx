import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import axiosInstance from '../api/axiosInstance'; // Import axiosInstance
import { jwtDecode } from 'jwt-decode'; // Import jwt-decode

interface AuthTokens {
    accessToken: string;
    refreshToken: string;
}

interface DecodedToken {
    sub: string; // User ID
    // Můžete přidat další pole z tokenu, která chcete používat, např. exp, iat, role atd.
}

interface AuthContextType {
    tokens: AuthTokens | null;
    userSub: string | null; // Identita uživatele (subject)
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (newTokens: AuthTokens) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [tokens, setTokens] = useState<AuthTokens | null>(null);
    const [userSub, setUserSub] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    // Pomocná funkce pro aktualizaci stavu a localStorage
    const updateAuthState = (newTokens: AuthTokens | null) => {
        if (newTokens && newTokens.accessToken) {
            try {
                const decodedToken = jwtDecode<DecodedToken>(newTokens.accessToken);
                setTokens(newTokens);
                setUserSub(decodedToken.sub);
                localStorage.setItem('authTokens', JSON.stringify(newTokens));
                localStorage.setItem('userSub', decodedToken.sub);
            } catch (e) {
                console.error("Chyba při dekódování tokenu během aktualizace stavu:", e);
                // Pokud dekódování selže, odhlásíme uživatele
                setTokens(null);
                setUserSub(null);
                localStorage.removeItem('authTokens');
                localStorage.removeItem('userSub');
            }
        } else { // Odhlášení
            setTokens(null);
            setUserSub(null);
            localStorage.removeItem('authTokens');
            localStorage.removeItem('userSub');
        }
    };

    useEffect(() => {
        // Počáteční načtení z localStorage
        try {
            const storedTokens = localStorage.getItem('authTokens');
            if (storedTokens) {
                const parsedTokens = JSON.parse(storedTokens) as AuthTokens;
                setTokens(parsedTokens);
                const storedUserSub = localStorage.getItem('userSub');
                if (storedUserSub) {
                    setUserSub(storedUserSub);
                } else if (parsedTokens.accessToken) {
                    try {
                        const decodedToken = jwtDecode<DecodedToken>(parsedTokens.accessToken);
                        setUserSub(decodedToken.sub);
                        localStorage.setItem('userSub', decodedToken.sub);
                    } catch (decodeError) {
                        console.error("Chyba při dekódování tokenu při startu:", decodeError);
                        localStorage.removeItem('authTokens');
                        localStorage.removeItem('userSub');
                        setTokens(null);
                        setUserSub(null);
                    }
                }
            }
        } catch (error) {
            console.error("Chyba při načítání tokenů z localStorage:", error);
            localStorage.removeItem('authTokens');
            localStorage.removeItem('userSub');
        } finally {
            setIsLoading(false);
        }

        // Naslouchání událostem od axiosInstance
        const handleTokensRefreshed = (event: Event) => {
            const { accessToken, refreshToken } = (event as CustomEvent).detail as AuthTokens;
            updateAuthState({ accessToken, refreshToken });
            console.log("AuthContext: Tokeny byly obnoveny.");
        };
        const handleForceLogout = () => {
            updateAuthState(null); // Odhlásí uživatele
            console.log("AuthContext: Vynucené odhlášení.");
        };

        window.addEventListener('tokensRefreshed', handleTokensRefreshed);
        window.addEventListener('forceLogout', handleForceLogout);

        return () => { // Cleanup
            window.removeEventListener('tokensRefreshed', handleTokensRefreshed);
            window.removeEventListener('forceLogout', handleForceLogout);
        };
    }, []); // Spustí se jednou po mountnutí

    const login = (newTokens: AuthTokens) => {
        updateAuthState(newTokens);
    };

    const logout = async () => {
        try {
            await axiosInstance.post('/auth/logout');
            console.log("Úspěšně odhlášeno i na serveru.");
        } catch (error) {
            console.error("Chyba při odhlašování na serveru:", error);
        } finally {
            updateAuthState(null); // Odhlášení na klientovi
        }
    };

    const isAuthenticated = !!tokens?.accessToken;

    return (
        <AuthContext.Provider value={{ tokens, userSub, isAuthenticated, isLoading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth musí být použit uvnitř AuthProvider');
    }
    return context;
};