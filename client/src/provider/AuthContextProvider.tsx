import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import { asyncLoadData } from '../services/asyncStorageService';

interface AuthState {
    isLoggedIn: boolean;
    isVerified: boolean;
    isAdmin: boolean;
}

interface AuthContextProps {
    authState: AuthState;
    login: (data: { isVerified: boolean; isAdmin: boolean }) => void;
    logout: () => void;
    updateVerified: (isVerified: boolean) => void;
}

const defaultAuthState: AuthState = {
    isLoggedIn: false,
    isVerified: false,
    isAdmin: false,
};

const AuthContext = createContext<AuthContextProps>({
    authState: defaultAuthState,
    login: () => { },
    logout: () => { },
    updateVerified: () => { },
});

export function AuthProvider({ children }: { children: ReactNode }) {
    const [authState, setAuthState] = useState<AuthState>(defaultAuthState);
    const [loading, setLoading] = useState(true);

    // Load the auth state from storage when the app starts
    // Otherwise it would return to the initial state (all false)
    useEffect(() => {
        const loadAuthState = async () => {
          try {
            // Load each piece of the auth state from storage
            const storedLoginState = await asyncLoadData('isLoggedIn');
            const storedVerifiedState = await asyncLoadData('isVerified');
            const storedAdminState = await asyncLoadData('isAdmin');
      
            // Convert the string values ("true"/"false") to booleans. If no value is stored, default to false.
            const isLoggedIn = storedLoginState === 'true';
            const isVerified = storedVerifiedState === 'true';
            const isAdmin = storedAdminState === 'true';
      
            // Update the auth state with the loaded values
            setAuthState({ isLoggedIn, isVerified, isAdmin });
          } catch (error) {
            console.error('Failed to load auth state:', error);
          } finally {
            setLoading(false);
          }
        };
        loadAuthState();
      }, []);

    const login = (data: { isVerified: boolean; isAdmin: boolean }) => {
        setAuthState({
            isLoggedIn: true,
            isVerified: data.isVerified,
            isAdmin: data.isAdmin,
        });
    };

    const logout = () => {
        setAuthState(defaultAuthState);
    };

    const updateVerified = (isVerified: boolean) => {
        setAuthState((prev) => ({ ...prev, isVerified }));
    };

    return (
        <AuthContext.Provider value={{ authState, login, logout, updateVerified }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
