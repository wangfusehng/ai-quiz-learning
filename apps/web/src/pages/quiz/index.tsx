import { View, Text, Textarea } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useEffect } from 'react'
import { createReport } from '../../api/client'
import { BackButton, Coin } from '../../components/Chrome'
import { consumeReplayFrom, clearReplayQuiz, peekReplayQuiz, useSession } from '../../store/session'
import type { SingleChoiceQuestion } from '../../types/quiz'

export default function QuizPage() {
  const quiz = useSession((s) => s.quiz)
  const replayQuiz = useSession((s) => s.replayQuiz)
  const currentIndex = useSession((s) => s.currentIndex)
  const selectedOptionId = useSession((s) => s.selectedOptionId)
  const revealed = useSession((s) => s.revealed)
  const shortText = useSession((s) => s.shortText)
  const inaccurate = useSession((s) => s.inaccurate)
  const selectOption = useSession((s) => s.selectOption)
  const revealCurrent = useSession((s) => s.revealCurrent)
  const goPrev = useSession((s) => s.goPrev)
  const goNext = useSession((s) => s.goNext)
  const setShortText = useSession((s) => s.setShortText)
  const setReport = useSession((s) => s.setReport)
  const saveShortAnswer = useSession((s) => s.saveShortAnswer)
  const markInaccurate = useSession((s) => s.markInaccurate)

  useEffect(() => {
    if (quiz) {
      clearReplayQuiz()
      return
    }
    const stored = peekReplayQuiz()
    if (stored) {
      replayQuiz(stored)
      return
    }
    Taro.redirectTo({ url: '/pages/index/index' })
  }, [quiz, replayQuiz])

  if (!quiz) {
    return null
  }

  const question = quiz.questions[currentIndex]
  const total = quiz.questions.length
  const minutes = quiz.meta.estimatedMinutes || 8
  const isLast = currentIndex === total - 1

  const finishReport = async () => {
    saveShortAnswer()
    const state = useSession.getState()
    const merged = state.answers
    const sheet = {
      quizId: quiz.quizId,
      startedAt: state.startedAt || new Date().toISOString(),
      submittedAt: new Date().toISOString(),
      answers: quiz.questions.map((item) => merged[item.id]).filter(Boolean),
    }
    try {
      Taro.showLoading({ title: '生成报告' })
      const report = await createReport({ quiz, answers: sheet })
      setReport(report)
      Taro.hideLoading()
      Taro.redirectTo({ url: '/pages/report/index' })
    } catch (err) {
      Taro.hideLoading()
      Taro.redirectTo({ url: '/pages/fail/index' })
      console.warn(err)
    }
  }

  const onPrimary = () => {
    if (question.type === 'short_answer') {
      saveShortAnswer()
      if (isLast) {
        finishReport()
        return
      }
      goNext()
      return
    }
    if (!revealed) {
      if (!selectedOptionId) return
      revealCurrent()
      return
    }
    if (isLast) {
      finishReport()
      return
    }
    goNext()
  }

  const primaryLabel = () => {
    if (question.type === 'short_answer') {
      return isLast ? '看通关报告' : '下一题'
    }
    if (!revealed) return '继续'
    return isLast ? '看通关报告' : '下一题'
  }

  const primaryDisabled =
    question.type === 'single_choice' ? !selectedOptionId && !revealed : false

  return (
    <View className='page'>
      <View className='nav'>
        <BackButton
          onClick={() => {
            const from = consumeReplayFrom()
            if (from === 'me') {
              Taro.redirectTo({ url: '/pages/me/index' })
              return
            }
            Taro.redirectTo({ url: '/pages/index/index' })
          }}
        />
        <Text className='nav-title'>
          第 {currentIndex + 1} / {total} 题
        </Text>
        <Coin text={`${minutes} min`} />
      </View>
      <View className='stage'>
        {question.type === 'single_choice' ? (
          <ChoiceBlock
            question={question}
            selectedOptionId={selectedOptionId}
            revealed={revealed}
            flagged={inaccurate.includes(question.id)}
            onSelect={selectOption}
            onFlag={() => markInaccurate(question.id)}
          />
        ) : (
          <View>
            <Text className='stem'>{question.stem}</Text>
            <View className='card'>
              <View className='field'>
                <Text className='field-label'>不打分，写完对照要点</Text>
                <Textarea
                  className='field-area'
                  value={shortText}
                  maxlength={800}
                  onInput={(e) => setShortText(e.detail.value)}
                />
              </View>
            </View>
            <Text className='hint'>
              可能盖到了：{question.rubric.keyPoints.join(' · ')}
            </Text>
          </View>
        )}
        <View className='btn-row' style={{ marginTop: 16 }}>
          <View className='btn btn-ghost' onClick={goPrev}>
            <Text className='btn-label'>上一题</Text>
          </View>
          <View
            className={primaryDisabled ? 'btn is-disabled' : 'btn'}
            onClick={primaryDisabled ? undefined : onPrimary}
          >
            <Text className='btn-label'>{primaryLabel()}</Text>
          </View>
        </View>
      </View>
    </View>
  )
}

function ChoiceBlock({
  question,
  selectedOptionId,
  revealed,
  flagged,
  onSelect,
  onFlag,
}: {
  question: SingleChoiceQuestion
  selectedOptionId: string | null
  revealed: boolean
  flagged: boolean
  onSelect: (id: string) => void
  onFlag: () => void
}) {
  const correct = selectedOptionId === question.correctOptionId
  return (
    <View>
      <View className='q-meta'>
        <Text className='q-meta-em'>{question.knowledgePoint}</Text>
        <Text>本题只打一个点</Text>
      </View>
      <Text className='stem'>{question.stem}</Text>
      <View className='opts'>
        {question.options.map((opt) => {
          let cls = 'opt'
          if (!revealed && selectedOptionId === opt.id) cls += ' is-on'
          if (revealed && opt.id === question.correctOptionId) cls += ' is-right'
          if (revealed && selectedOptionId === opt.id && opt.id !== question.correctOptionId) {
            cls += ' is-wrong'
          }
          if (
            revealed &&
            opt.id !== question.correctOptionId &&
            opt.id !== selectedOptionId
          ) {
            cls += ' is-fade'
          }
          return (
            <View
              key={opt.id}
              className={cls}
              onClick={() => {
                if (!revealed) onSelect(opt.id)
              }}
            >
              {opt.text}
            </View>
          )
        })}
      </View>
      {revealed ? (
        <View>
          <View className={correct ? 'ok-bar' : 'ok-bar is-miss'}>
            {correct ? '答对了！' : '这题没答对'}
          </View>
          <View className='explain'>
            <Text className='explain-b'>解析</Text>
            <Text>{question.explanation}</Text>
            <View className='quote'>
              原句 · {question.sourceQuote.locator}：「{question.sourceQuote.text}」
            </View>
          </View>
          <View className='linkish' onClick={onFlag}>
            {flagged ? '已记下这题不准' : '这题出得不准'}
          </View>
        </View>
      ) : null}
    </View>
  )
}
