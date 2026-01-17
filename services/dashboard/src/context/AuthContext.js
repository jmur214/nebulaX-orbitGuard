import { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/router';

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const router = useRouter();

    // Simulated "Session" persistence
    useEffect(() => {
        const storedUser = localStorage.getItem('astra_user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, []);

    const login = (username, password, targetRoute) => {
        // HARDCODED CREDENTIALS FOR SIMULATION
        const CREDENTIALS = {
            'syndicate': { pass: 'hunter2', role: 'RED_TEAM', route: '/red' },
            'analyst': { pass: 'defense', role: 'BLUE_TEAM', route: '/blue' },
            'operator': { pass: 'orbit', role: 'SPACE_CMD', route: '/space' },
            'director': { pass: 'astra', role: 'FUSION', route: '/fusion' }
        };

        const account = CREDENTIALS[username];

        if (account && account.pass === password) {
            const userData = { username, role: account.role };
            setUser(userData);
            localStorage.setItem('astra_user', JSON.stringify(userData));

            // Redirect to target or their default role route
            router.push(targetRoute || account.route);
            return { success: true };
        } else {
            return { success: false, message: "INVALID CREDENTIALS" };
        }
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('astra_user');
        router.push('/');
    };

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
