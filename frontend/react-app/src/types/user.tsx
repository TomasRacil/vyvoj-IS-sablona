export interface Role {
    id: string;
    name: string;
    description: string | null;
}

export interface User {
    created_at: string;
    email: string;
    id: string;
    username: string;
    roles: Role[];
}

export interface UserCreationData {
    username: string;
    email: string;
    password: string;
}