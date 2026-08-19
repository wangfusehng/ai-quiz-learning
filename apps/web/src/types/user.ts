import type { QuizDocument } from './quiz'

export type AuthUser = {
  id: number
  nickname: string | null
  avatarUrl: string | null
  wechatConnected: boolean
}

export type AuthResponse = {
  token: string
  user: AuthUser
}

export type QuizRecordItem = {
  id: number
  quizId: string
  title: string
  correct: number
  total: number
  completedAt: string
  quiz?: QuizDocument | null
}

export type QuizRecordDetail = QuizRecordItem & {
  quiz: QuizDocument
}
