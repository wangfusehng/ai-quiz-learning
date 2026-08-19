import Taro from '@tarojs/taro'
import { create } from 'zustand'
import type { AuthUser } from '../types/user'

const TOKEN_KEY = 'guan_ka_xue_token'

type AuthStatus = 'unknown' | 'connected' | 'offline'

interface AuthState {
  token: string | null
  user: AuthUser | null
  status: AuthStatus
  setSession: (token: string, user: AuthUser) => void
  setUser: (user: AuthUser) => void
  setOffline: () => void
  hydrateToken: () => string | null
}

export function readStoredToken(): string | null {
  try {
    const value = Taro.getStorageSync(TOKEN_KEY)
    return typeof value === 'string' && value ? value : null
  } catch {
    return null
  }
}

export const useAuth = create<AuthState>((set) => ({
  token: readStoredToken(),
  user: null,
  status: 'unknown',
  setSession: (token, user) => {
    Taro.setStorageSync(TOKEN_KEY, token)
    set({ token, user, status: 'connected' })
  },
  setUser: (user) => set({ user }),
  setOffline: () => set({ status: 'offline' }),
  hydrateToken: () => readStoredToken(),
}))
