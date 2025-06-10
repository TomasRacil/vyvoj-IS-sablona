export interface User {
    created_at: string;
    email: string;
    id: string;
    username: string; // Datum jako string (ISO formát z API)
}

export interface UserCreationData {
    username: string;
    email: string;
    password: string;
}