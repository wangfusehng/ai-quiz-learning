import Taro from '@tarojs/taro'
import type { AnswerSheet, QuizDocument, ReportDocument } from '../types/quiz'
import { ApiError } from '../types/quiz'
import type { AuthResponse, AuthUser, QuizRecordDetail, QuizRecordItem } from '../types/user'
import { readStoredToken, useAuth } from '../store/auth'

function baseUrl(): string {
  if (process.env.TARO_ENV === 'h5') {
    return ''
  }
  return 'http://127.0.0.1:8000'
}

async function refreshWeappToken(): Promise<boolean> {
  if (process.env.TARO_ENV !== 'weapp') {
    return false
  }
  try {
    const login = await Taro.login()
    if (!login.code) {
      return false
    }
    const res = await Taro.request({
      url: `${baseUrl()}/v1/auth/wechat`,
      method: 'POST',
      data: { code: login.code },
      header: { 'Content-Type': 'application/json' },
      timeout: 15000,
    })
    if (res.statusCode >= 400) {
      return false
    }
    const data = res.data as AuthResponse
    if (!data?.token) {
      return false
    }
    useAuth.getState().setSession(data.token, data.user)
    return true
  } catch {
    return false
  }
}

async function request<T>(option: Taro.request.Option, retry = true): Promise<T> {
  const token = readStoredToken()
  const res = await Taro.request({
    ...option,
    url: `${baseUrl()}${option.url}`,
    header: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(option.header || {}),
    },
  })
  if (res.statusCode === 401 && retry) {
    const ok = await refreshWeappToken()
    if (ok) {
      return request<T>(option, false)
    }
  }
  if (res.statusCode >= 400) {
    const payload = res.data as { error?: string }
    throw new ApiError(payload?.error || 'upstream', res.statusCode)
  }
  return res.data as T
}

export function createQuiz(payload: { title?: string; text: string }) {
  return request<QuizDocument>({
    url: '/v1/quizzes',
    method: 'POST',
    data: payload,
    timeout: 120000,
  })
}

export function createReport(payload: { quiz: QuizDocument; answers: AnswerSheet }) {
  return request<ReportDocument>({
    url: '/v1/reports',
    method: 'POST',
    data: payload,
    timeout: 90000,
  })
}

export function loginWechat(code: string) {
  return request<AuthResponse>({
    url: '/v1/auth/wechat',
    method: 'POST',
    data: { code },
    timeout: 15000,
  })
}

export function fetchMe() {
  return request<AuthUser>({
    url: '/v1/me',
    method: 'GET',
    timeout: 15000,
  })
}

export function updateMe(payload: { nickname?: string; avatarUrl?: string }) {
  return request<AuthUser>({
    url: '/v1/me',
    method: 'PUT',
    data: payload,
    timeout: 15000,
  })
}

export function fetchRecords() {
  return request<{ items: QuizRecordItem[] }>({
    url: '/v1/records',
    method: 'GET',
    timeout: 15000,
  })
}

export function fetchRecord(id: number) {
  return request<QuizRecordDetail>({
    url: `/v1/records/${id}`,
    method: 'GET',
    timeout: 15000,
  })
}

export async function silentLogin(): Promise<boolean> {
  if (process.env.TARO_ENV !== 'weapp') {
    useAuth.getState().setOffline()
    return false
  }
  const ok = await refreshWeappToken()
  if (!ok) {
    useAuth.getState().setOffline()
  }
  return ok
}
