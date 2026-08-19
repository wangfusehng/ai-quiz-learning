import Taro from '@tarojs/taro'
import type { AnswerSheet, QuizDocument, ReportDocument } from '../types/quiz'
import { ApiError } from '../types/quiz'

function baseUrl(): string {
  if (process.env.TARO_ENV === 'h5') {
    return ''
  }
  return 'http://127.0.0.1:8000'
}

async function request<T>(option: Taro.request.Option): Promise<T> {
  const res = await Taro.request({
    ...option,
    url: `${baseUrl()}${option.url}`,
    header: {
      'Content-Type': 'application/json',
      ...(option.header || {}),
    },
  })
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
