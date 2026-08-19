import { Text, View } from '@tarojs/components'
import Taro, { useRouter } from '@tarojs/taro'
import { useEffect, useState } from 'react'
import { deleteMistake, fetchMistake, reviewMistake } from '../../../api/client'
import { BackButton } from '../../../components/Chrome'
import type { MistakeItem } from '../../../types/user'
import './index.scss'

export default function MistakeDetailPage() {
  const router = useRouter()
  const id = Number(router.params.id)
  const [item, setItem] = useState<MistakeItem | null>(null)
  const [mode, setMode] = useState<'review' | 'practice'>('review')
  const [selected, setSelected] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!Number.isFinite(id) || id <= 0) {
      Taro.showToast({ title: '这题找不到了', icon: 'none' })
      Taro.navigateBack()
      return
    }
    const load = async () => {
      try {
        const detail = await fetchMistake(id)
        setItem(detail)
        setMode('review')
        setSelected(null)
      } catch {
        Taro.showToast({ title: '这题找不到了', icon: 'none' })
        Taro.navigateBack()
      }
    }
    load()
  }, [id])

  if (!item) {
    return null
  }

  const revealed = mode === 'review'
  const chosenId = mode === 'practice' ? selected : item.chosenOptionId
  const submitDisabled = mode === 'practice' && !selected

  const startPractice = () => {
    setMode('practice')
    setSelected(null)
  }

  const cancelPractice = () => {
    setMode('review')
    setSelected(null)
  }

  const submit = async () => {
    if (!selected || busy) return
    setBusy(true)
    try {
      const result = await reviewMistake(item.id, selected)
      if (result.mastered) {
        Taro.showToast({ title: '这题会了，移出错题本了', icon: 'none' })
        setTimeout(() => Taro.navigateBack(), 400)
        return
      }
      if (result.item) {
        setItem(result.item)
      }
      setMode('review')
      setSelected(null)
    } catch {
      Taro.showToast({ title: '没对上，再试一次', icon: 'none' })
    } finally {
      setBusy(false)
    }
  }

  const remove = async () => {
    if (busy) return
    setBusy(true)
    try {
      await deleteMistake(item.id)
      Taro.showToast({ title: '已移出', icon: 'none' })
      setTimeout(() => Taro.navigateBack(), 300)
    } catch {
      setBusy(false)
      Taro.showToast({ title: '没移出去，再试一次', icon: 'none' })
    }
  }

  return (
    <View className='page'>
      <View className='nav'>
        <BackButton onClick={() => Taro.navigateBack()} />
        <Text className='nav-title'>错题</Text>
        <View style={{ width: 40 }} />
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
            if (revealed && chosenId === opt.id && opt.id !== item.correctOptionId) {
              cls += ' is-wrong'
            }
            if (
              revealed &&
              opt.id !== item.correctOptionId &&
              opt.id !== chosenId
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
            <View className='ok-bar is-miss'>这题没答对</View>
            <View className='explain'>
              <Text className='explain-b'>解析</Text>
              <Text>{item.explanation}</Text>
              <View className='quote'>
                原句 · {item.sourceQuote.locator}：「{item.sourceQuote.text}」
              </View>
            </View>
          </View>
        ) : null}
        <View className='btn-row mistake-actions'>
          {mode === 'review' ? (
            <>
              <View className='btn btn-ghost' onClick={busy ? undefined : remove}>
                <Text className='btn-label'>移出</Text>
              </View>
              <View className='btn' onClick={busy ? undefined : startPractice}>
                <Text className='btn-label'>再做一次</Text>
              </View>
            </>
          ) : (
            <>
              <View className='btn btn-ghost' onClick={busy ? undefined : cancelPractice}>
                <Text className='btn-label'>先看看</Text>
              </View>
              <View
                className={submitDisabled || busy ? 'btn is-disabled' : 'btn'}
                onClick={submitDisabled || busy ? undefined : submit}
              >
                <Text className='btn-label'>对一下</Text>
              </View>
            </>
          )}
        </View>
      </View>
    </View>
  )
}
