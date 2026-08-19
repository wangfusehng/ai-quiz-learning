import { Text, View } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useEffect, useState } from 'react'
import { fetchMistakes, reviewMistake, silentLogin } from '../../../api/client'
import { BackButton, Coin } from '../../../components/Chrome'
import { useAuth } from '../../../store/auth'
import type { MistakeItem } from '../../../types/user'
import './index.scss'

const isWeapp = process.env.TARO_ENV === 'weapp'

export default function MistakePracticePage() {
  const [items, setItems] = useState<MistakeItem[]>([])
  const [index, setIndex] = useState(0)
  const [selected, setSelected] = useState<string | null>(null)
  const [revealed, setRevealed] = useState(false)
  const [busy, setBusy] = useState(false)
  const [correctCount, setCorrectCount] = useState(0)
  const [done, setDone] = useState(false)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const load = async () => {
      if (!isWeapp) {
        useAuth.getState().setOffline()
        setReady(true)
        return
      }
      if (useAuth.getState().status !== 'connected') {
        const ok = await silentLogin()
        if (!ok) {
          setReady(true)
          return
        }
      }
      try {
        const data = await fetchMistakes()
        setItems(data.items)
      } catch {
        useAuth.getState().setOffline()
      } finally {
        setReady(true)
      }
    }
    load()
  }, [])

  if (!ready) {
    return null
  }

  if (!items.length || done) {
    const total = items.length
    const leftover = Math.max(0, total - correctCount)
    return (
      <View className='page'>
        <View className='nav'>
          <BackButton onClick={() => Taro.navigateBack()} />
          <Text className='nav-title'>练习错题</Text>
          <View style={{ width: 40 }} />
        </View>
        <View className='stage'>
          <View className='card practice-done'>
            <Text className='practice-done-title'>
              {total === 0 ? '还没有能练的错题。' : '这轮练完了'}
            </Text>
            <Text className='practice-done-hint'>
              {total === 0
                ? '打关时没答对的选择题会进错题本，再从这里开练。'
                : leftover === 0
                  ? `做对 ${correctCount} 题，都已经移出错题本了。`
                  : `做对 ${correctCount} 题，已经移出。还没对的 ${leftover} 题仍在本子里。`}
            </Text>
          </View>
          <View
            className='btn'
            style={{ marginTop: 16 }}
            onClick={() => Taro.redirectTo({ url: '/pages/mistakes/index' })}
          >
            <Text className='btn-label'>回到错题本</Text>
          </View>
        </View>
      </View>
    )
  }

  const item = items[index]
  const total = items.length
  const submitDisabled = !selected && !revealed
  const isLast = index >= total - 1
  const isCorrect = revealed && selected === item.correctOptionId

  const submit = async () => {
    if (!selected || revealed || busy) return
    setBusy(true)
    try {
      const result = await reviewMistake(item.id, selected)
      if (result.mastered) {
        setCorrectCount((count) => count + 1)
      } else if (result.item) {
        setItems((rows) => rows.map((row, i) => (i === index ? result.item! : row)))
      }
      setRevealed(true)
    } catch {
      Taro.showToast({ title: '没对上，再试一次', icon: 'none' })
    } finally {
      setBusy(false)
    }
  }

  const goNext = () => {
    if (isLast) {
      setDone(true)
      return
    }
    setIndex((current) => current + 1)
    setSelected(null)
    setRevealed(false)
  }

  const onPrimary = () => {
    if (!revealed) {
      submit()
      return
    }
    goNext()
  }

  return (
    <View className='page'>
      <View className='nav'>
        <BackButton onClick={() => Taro.navigateBack()} />
        <Text className='nav-title'>
          第 {index + 1} / {total} 题
        </Text>
        <Coin text='错题' />
      </View>
      <View className='stage'>
        <View className='q-meta'>
          <Text className='q-meta-em'>{item.knowledgePoint}</Text>
          <Text>{item.title}</Text>
        </View>
        <Text className='stem'>{item.stem}</Text>
        <View className='opts'>
          {item.options.map((opt) => {
            let cls = 'opt'
            if (!revealed && selected === opt.id) cls += ' is-on'
            if (revealed && opt.id === item.correctOptionId) cls += ' is-right'
            if (revealed && selected === opt.id && opt.id !== item.correctOptionId) {
              cls += ' is-wrong'
            }
            if (
              revealed &&
              opt.id !== item.correctOptionId &&
              opt.id !== selected
            ) {
              cls += ' is-fade'
            }
            return (
              <View
                key={opt.id}
                className={cls}
                onClick={() => {
                  if (!revealed) setSelected(opt.id)
                }}
              >
                {opt.text}
              </View>
            )
          })}
        </View>
        {revealed ? (
          <View>
            <View className={isCorrect ? 'ok-bar' : 'ok-bar is-miss'}>
              {isCorrect ? '答对了，移出错题本了' : '这题没答对'}
            </View>
            <View className='explain'>
              <Text className='explain-b'>解析</Text>
              <Text>{item.explanation}</Text>
              <View className='quote'>
                原句 · {item.sourceQuote.locator}：「{item.sourceQuote.text}」
              </View>
            </View>
          </View>
        ) : null}
        <View className='btn-row' style={{ marginTop: 16 }}>
          <View
            className={submitDisabled || busy ? 'btn is-disabled' : 'btn'}
            onClick={submitDisabled || busy ? undefined : onPrimary}
          >
            <Text className='btn-label'>
              {!revealed ? '对一下' : isLast ? '看这轮结果' : '下一题'}
            </Text>
          </View>
        </View>
      </View>
    </View>
  )
}
