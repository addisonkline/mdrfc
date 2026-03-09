import { createContext, useCallback, useEffect, useState, type ReactNode } from 'react';
import type { User } from '../types';
import { login as apiLogin, signup as apiSignup } from '../api/auth';
import { getMe } from '../api/users';
import { getStoredToken, setStoredToken, clearStoredToken } from '../api/client';
import type { SignupData, PostSignupResponse } from '../types';

export interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  signup: (data: SignupData) => Promise<PostSignupResponse>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(getStoredToken());
  const [isLoading, setIsLoading] = useState(!!getStoredToken());

  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return;
    }
    getMe()
      .then(setUser)
      .catch(() => {
        clearStoredToken();
        setToken(null);
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, [token]);

  const login = useCallback(async (username: string, password: string) => {
    const result = await apiLogin(username, password);
    setStoredToken(result.access_token);
    setToken(result.access_token);
    const me = await getMe();
    setUser(me);
  }, []);

  const signup = useCallback(async (data: SignupData) => {
    return apiSignup(data);
  }, []);

  const logout = useCallback(() => {
    clearStoredToken();
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
