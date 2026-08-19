import { create } from 'zustand'
import type { AnswerItem, QuizDocument, ReportDocument } from '../types/quiz'

export const SAMPLE_MATERIAL =
  '卡尼曼讲过，人对确定损失的厌恶，常常大过对同等收益的喜欢。看完视频觉得懂了，转头却说不清损失厌恶到底在怕什么。真正的难点不是记术语，而是把确定亏掉和确定赚到放在同一笔钱上对比。看懂是熟悉感，能讲出来才是提取练习。测验效应说明，主动回忆比再看一遍更有助于记住关键概念。材料强调这不是鼓励冒险亏损，也不是通货膨胀的另一种说法。同样一笔钱，确定亏掉往往比确定赚到更扎心。熟悉感会让人误以为已经掌握，直到被提问才发现讲不完整。'

interface SessionState {
  material: string
  title: string
  quiz: QuizDocument | null
  answers: Record<string, AnswerItem>
  currentIndex: number
  selectedOptionId: string | null
  revealed: boolean
  shortText: string
  report: ReportDocument | null
  startedAt: string | null
  cancelled: boolean
  inaccurate: string[]
  setMaterial: (value: string) => void
  setTitle: (value: string) => void
  setShortText: (value: string) => void
  beginGenerate: () => void
  setQuiz: (quiz: QuizDocument) => void
  selectOption: (optionId: string) => void
  revealCurrent: () => void
  markInaccurate: (questionId: string) => void
  goPrev: () => void
  goNext: () => void
  setReport: (report: ReportDocument) => void
  saveShortAnswer: () => void
  cancelGenerate: () => void
  resetAll: () => void
}

export const useSession = create<SessionState>((set, get) => ({
  material: SAMPLE_MATERIAL,
  title: '',
  quiz: null,
  answers: {},
  currentIndex: 0,
  selectedOptionId: null,
  revealed: false,
  shortText: '',
  report: null,
  startedAt: null,
  cancelled: false,
  inaccurate: [],
  setMaterial: (value) => set({ material: value }),
  setTitle: (value) => set({ title: value }),
  setShortText: (value) => set({ shortText: value }),
  beginGenerate: () =>
    set({
      quiz: null,
      answers: {},
      currentIndex: 0,
      selectedOptionId: null,
      revealed: false,
      shortText: '',
      report: null,
      startedAt: new Date().toISOString(),
      cancelled: false,
      inaccurate: [],
    }),
  setQuiz: (quiz) => set({ quiz, currentIndex: 0, answers: {}, revealed: false, selectedOptionId: null }),
  selectOption: (optionId) => set({ selectedOptionId: optionId }),
  revealCurrent: () => {
    const { quiz, currentIndex, selectedOptionId, answers } = get()
    const question = quiz?.questions[currentIndex]
    if (!question || question.type !== 'single_choice' || !selectedOptionId) return
    set({
      revealed: true,
      answers: {
        ...answers,
        [question.id]: {
          questionId: question.id,
          type: 'single_choice',
          optionId: selectedOptionId,
        },
      },
    })
  },
  markInaccurate: (questionId) =>
    set((state) => ({
      inaccurate: state.inaccurate.includes(questionId)
        ? state.inaccurate
        : [...state.inaccurate, questionId],
    })),
  goPrev: () => {
    const { currentIndex, quiz, answers } = get()
    if (currentIndex <= 0 || !quiz) return
    const prev = quiz.questions[currentIndex - 1]
    const saved = answers[prev.id]
    set({
      currentIndex: currentIndex - 1,
      revealed: Boolean(saved),
      selectedOptionId: saved && saved.type === 'single_choice' ? saved.optionId : null,
      shortText: saved && saved.type === 'short_answer' ? saved.text : get().shortText,
    })
  },
  goNext: () => {
    const { currentIndex, quiz, answers } = get()
    if (!quiz || currentIndex >= quiz.questions.length - 1) return
    const next = quiz.questions[currentIndex + 1]
    const saved = answers[next.id]
    set({
      currentIndex: currentIndex + 1,
      revealed: Boolean(saved) && next.type === 'single_choice',
      selectedOptionId: saved && saved.type === 'single_choice' ? saved.optionId : null,
    })
  },
  setReport: (report) => set({ report }),
  saveShortAnswer: () => {
    const { quiz, currentIndex, shortText, answers } = get()
    const question = quiz?.questions[currentIndex]
    if (!question || question.type !== 'short_answer') return
    set({
      answers: {
        ...answers,
        [question.id]: {
          questionId: question.id,
          type: 'short_answer',
          text: shortText,
        },
      },
    })
  },
  cancelGenerate: () => set({ cancelled: true }),
  resetAll: () =>
    set({
      quiz: null,
      answers: {},
      currentIndex: 0,
      selectedOptionId: null,
      revealed: false,
      shortText: '',
      report: null,
      startedAt: null,
      cancelled: false,
      inaccurate: [],
    }),
}))
