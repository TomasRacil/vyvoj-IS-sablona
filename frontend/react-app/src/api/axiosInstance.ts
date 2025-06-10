import axios, { InternalAxiosRequestConfig, AxiosError } from 'axios';

// Funkce pro získání tokenů z localStorage
const getAuthTokensFromStorage = (): { accessToken: string | null; refreshToken: string | null } => {
    const storedTokens = localStorage.getItem('authTokens');
    if (storedTokens) {
        try {
            const tokens = JSON.parse(storedTokens);
            return {
                accessToken: tokens.accessToken || null,
                refreshToken: tokens.refreshToken || null,
            };
        } catch (e) {
            console.error("Chyba při parsování authTokens z localStorage", e);
            // Vyčistit poškozená data
            localStorage.removeItem('authTokens');
            localStorage.removeItem('userSub');
            return { accessToken: null, refreshToken: null };
        }
    }
    return { accessToken: null, refreshToken: null };
};

// Funkce pro uložení tokenů do localStorage
const setAuthTokensInStorage = (accessToken: string, refreshToken: string) => {
    const authData = { accessToken, refreshToken };
    localStorage.setItem('authTokens', JSON.stringify(authData));
    // userSub bude aktualizován AuthContextem přes událost
};

const axiosInstance = axios.create({
    baseURL: '/api/v1'
});

// Request Interceptor: Přidává AccessToken do hlavičky
axiosInstance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const { accessToken } = getAuthTokensFromStorage();
        // Nepřidávejte Authorization hlavičku pro refresh endpoint, pokud to není vyžadováno
        if (accessToken && config.headers && config.url !== '/auth/refresh') {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

let isRefreshing = false;
let failedQueue: Array<{ resolve: (value: string | null) => void; reject: (reason?: AxiosError | Error | null) => void }> = [];

const processQueue = (error: AxiosError | null, token: string | null = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

// Response Interceptor: Zpracovává expiraci tokenu a refresh
axiosInstance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        // Pokud je chyba 401, nejedná se o opakovaný pokus a nejde o refresh endpoint samotný
        if (error.response?.status === 401 && originalRequest.url !== '/api/v1/auth/refresh' && !originalRequest._retry) {
            if (isRefreshing) {
                // Pokud již probíhá refresh, zařadíme požadavek do fronty
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then(token => {
                    if (originalRequest.headers) originalRequest.headers['Authorization'] = 'Bearer ' + token;
                    return axiosInstance(originalRequest);
                }).catch(err => Promise.reject(err));
            }

            originalRequest._retry = true;
            isRefreshing = true;

            const { refreshToken: currentRefreshToken } = getAuthTokensFromStorage();

            if (currentRefreshToken) {
                try {
                    // Pro refresh endpoint použijeme globální axios, abychom se vyhnuli smyčce interceptorů,
                    // a nastavíme hlavičku Authorization s refresh tokenem.
                    const refreshResponse = await axios.post('/api/v1/auth/refresh', {}, { // Tělo může být prázdné
                        headers: {
                            'Authorization': `Bearer ${currentRefreshToken}`
                        }
                    });
                    // Backend vrací pouze nový access_token
                    const newAccessToken = refreshResponse.data.access_token;

                    setAuthTokensInStorage(newAccessToken, currentRefreshToken);

                    // Odešlete událost, aby AuthContext mohl aktualizovat svůj stav
                    window.dispatchEvent(new CustomEvent('tokensRefreshed', { detail: { accessToken: newAccessToken } }));

                    if (originalRequest.headers) originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
                    processQueue(null, newAccessToken);
                    return axiosInstance(originalRequest); // Zopakujte původní požadavek
                } catch (refreshError) {
                    processQueue(refreshError as AxiosError, null);
                    window.dispatchEvent(new CustomEvent('forceLogout')); // Událost pro odhlášení
                    return Promise.reject(refreshError);
                } finally {
                    isRefreshing = false;
                }
            } else { // Není refresh token
                isRefreshing = false;
                window.dispatchEvent(new CustomEvent('forceLogout'));
                return Promise.reject(error);
            }
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;