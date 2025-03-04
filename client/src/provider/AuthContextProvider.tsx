// AuthContextProvider.tsx
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
  login: () => {},
  logout: () => {},
  updateVerified: () => {},
});

// This variable will store the logout function so it can be used outside of components.
let globalLogout: (() => void) | null = null;
export const setGlobalLogout = (logoutFn: () => void) => {
  globalLogout = logoutFn;
};
export const getGlobalLogout = () => globalLogout;

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>(defaultAuthState);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAuthState = async () => {
      try {
        const storedLoginState = await asyncLoadData('isLoggedIn');
        const storedVerifiedState = await asyncLoadData('isVerified');
        const storedAdminState = await asyncLoadData('isAdmin');

        const isLoggedIn = storedLoginState === 'true';
        const isVerified = storedVerifiedState === 'true';
        const isAdmin = storedAdminState === 'true';

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

  // Register the logout function globally so it can be used outside of components.
  useEffect(() => {
    setGlobalLogout(logout);
  }, []);

  return (
    <AuthContext.Provider value={{ authState, login, logout, updateVerified }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}