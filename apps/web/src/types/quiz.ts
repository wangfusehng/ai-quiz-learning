export type QuestionType = 'single_choice' | 'short_answer'

export interface SourceQuote {
  text: string
  locator: string
}

export interface Option {
  id: string
  text: string
}

export interface SingleChoiceQuestion {
  id: string
  type: 'single_choice'
  stem: string
  options: Option[]
  correctOptionId: string
  explanation: string
  sourceQuote: SourceQuote
  knowledgePoint: string
}

export interface ShortAnswerQuestion {
  id: string
  type: 'short_answer'
  stem: string
  rubric: { keyPoints: string[] }
  explanation: string
  sourceQuote: SourceQuote
  knowledgePoint: string
}

export type Question = SingleChoiceQuestion | ShortAnswerQuestion

export interface QuizDocument {
  schemaVersion: '1'
  quizId: string
  source: {
    type: 'text'
    title: string
    excerpt: string
    charCount: number
  }
  meta: {
    model: string
    thinking: boolean
    questionCount: number
    estimatedMinutes: number
    aiGenerated: boolean
  }
  questions: Question[]
}

export interface ChoiceAnswer {
  questionId: string
  type: 'single_choice'
  optionId: string
}

export interface ShortAnswer {
  questionId: string
  type: 'short_answer'
  text: string
}

export type AnswerItem = ChoiceAnswer | ShortAnswer

export interface AnswerSheet {
  quizId: string
  answers: AnswerItem[]
  startedAt: string
  submittedAt: string
}

export interface ReportDocument {
  schemaVersion: '1'
  quizId: string
  aiGenerated: boolean
  headline: string
  oneLiner: string
  pointsBitten: string[]
  stillFuzzy: string[]
  goldQuote: SourceQuote
  invite: string
  scoreHint: {
    correct: number
    total: number
    shortAnswerNote: string
  }
}

export class ApiError extends Error {
  constructor(public error: string, public statusCode: number) {
    super(error)
  }
}
