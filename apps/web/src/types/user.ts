import type { Option, QuizDocument, SourceQuote } from './quiz'

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

export type MistakeItem = {
  id: number
  quizId: string
  questionId: string
  title: string
  knowledgePoint: string
  stem: string
  options: Option[]
  correctOptionId: string
  chosenOptionId: string
  explanation: string
  sourceQuote: SourceQuote
  completedAt: string
}

export type MistakeReviewResult = {
  mastered: boolean
  item: MistakeItem | null
}
