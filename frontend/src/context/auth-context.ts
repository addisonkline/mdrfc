import { createContext } from 'react';
import type { PostSignupResponse, SignupData, User } from '../types';

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
