import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useEffect, useRef, useState } from 'react'
import { createQuiz } from '../../api/client'
import { BackButton } from '../../components/Chrome'
import { ApiError } from '../../types/quiz'
import { useSession } from '../../store/session'

function pad(n: number) {
  return n.toString().padStart(2, '0')
}

function waitCopy(seconds: number) {
  if (seconds < 5) return '正在阅读材料'
  if (seconds < 20) return '正在出概念辨析题和干扰项'
  return '仍在生成，长文会多等一会儿'
}

export default function WaitPage() {
  const material = useSession((s) => s.material)
  const title = useSession((s) => s.title)
  const setQuiz = useSession((s) => s.setQuiz)
  const cancelGenerate = useSession((s) => s.cancelGenerate)
  const [seconds, setSeconds] = useState(0)
  const alive = useRef(true)

  useEffect(() => {
    alive.current = true
    const timer = setInterval(() => setSeconds((s) => s + 1), 1000)
    createQuiz({ title: title || undefined, text: material })
      .then((quiz) => {
        if (!alive.current || useSession.getState().cancelled) return
        setQuiz(quiz)
        Taro.redirectTo({ url: '/pages/quiz/index' })
      })
      .catch((err: ApiError | Error) => {
        if (!alive.current || useSession.getState().cancelled) return
        Taro.redirectTo({ url: '/pages/fail/index' })
        console.warn(err)
      })
    return () => {
      alive.current = false
      clearInterval(timer)
    }
  }, [material, setQuiz, title])

  const onCancel = () => {
    cancelGenerate()
    alive.current = false
    Taro.navigateBack()
  }

  return (
    <View className='page'>
      <View className='nav'>
        <BackButton onClick={onCancel} />
        <Text className='nav-title'>正在出题</Text>
        <View style={{ width: 40 }} />
      </View>
      <View className='stage'>
        <View className='wait-art'>
          <View className='blob' />
        </View>
        <Text className='timer'>
          {pad(Math.floor(seconds / 60))}:{pad(seconds % 60)}
        </Text>
        <Text className='stem'>{waitCopy(seconds)}</Text>
        <Text className='hint center-hint'>请留在这一页。切走可能中断。没有假进度条。</Text>
        <View className='btn btn-ghost' style={{ marginTop: 20 }} onClick={onCancel}>
          <Text className='btn-label'>取消本次</Text>
        </View>
      </View>
    </View>
  )
}
