import { Button, Image, Input, Text, View } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import { useMemo, useState } from 'react'
import { fetchMe, fetchRecord, fetchRecords, silentLogin, updateMe } from '../../api/client'
import { TabBar } from '../../components/TabBar'
import { useAuth } from '../../store/auth'
import { stashReplayQuiz, useSession } from '../../store/session'
import type { QuizRecordItem } from '../../types/user'
import './index.scss'

const isWeapp = process.env.TARO_ENV === 'weapp'

function accuracyText(correct: number, total: number) {
  if (total <= 0) return '0%'
  return `${Math.round((correct / total) * 100)}%`
}

export default function MePage() {
  const user = useAuth((s) => s.user)
  const status = useAuth((s) => s.status)
  const setUser = useAuth((s) => s.setUser)
  const nickname = user?.nickname || '同学'
  const connected = status === 'connected'
  const [records, setRecords] = useState<QuizRecordItem[]>([])

  useDidShow(() => {
    const load = async () => {
      if (!isWeapp) {
        useAuth.getState().setOffline()
        setRecords([])
        return
      }
      if (useAuth.getState().status !== 'connected') {
        const ok = await silentLogin()
        if (!ok) {
          setRecords([])
          return
        }
      }
      try {
        const me = await fetchMe()
        setUser(me)
        const data = await fetchRecords()
        setRecords(data.items)
      } catch {
        useAuth.getState().setOffline()
        setRecords([])
      }
    }
    load()
  })

  const stats = useMemo(() => {
    const times = records.length
    const correct = records.reduce((sum, item) => sum + item.correct, 0)
    const total = records.reduce((sum, item) => sum + item.total, 0)
    return {
      times,
      correct,
      rate: accuracyText(correct, total),
    }
  }, [records])

  const saveNickname = async (value: string) => {
    const next = value.trim()
    if (!next || !connected) {
      return
    }
    try {
      const me = await updateMe({ nickname: next })
      setUser(me)
    } catch {
      Taro.showToast({ title: '没存上，再试一次', icon: 'none' })
    }
  }

  const saveAvatar = async (url: string) => {
    if (!url || !connected) {
      return
    }
    try {
      const me = await updateMe({ avatarUrl: url })
      setUser(me)
    } catch {
      Taro.showToast({ title: '头像没存上', icon: 'none' })
    }
  }

  const replay = async (item: QuizRecordItem) => {
    try {
      Taro.showLoading({ title: '打开原题' })
      let quiz = item.quiz
      if (!quiz?.questions?.length) {
        const detail = await fetchRecord(item.id)
        quiz = detail.quiz
      }
      if (!quiz?.questions?.length) {
        throw new Error('empty')
      }
      useSession.getState().replayQuiz(quiz)
      stashReplayQuiz(quiz, 'me')
      Taro.hideLoading()
      await Taro.redirectTo({ url: '/pages/quiz/index' })
    } catch {
      Taro.hideLoading()
      Taro.showToast({ title: '这关暂时打不开', icon: 'none' })
    }
  }

  const avatarInner = user?.avatarUrl ? (
    <Image className='me-avatar' src={user.avatarUrl} mode='aspectFill' />
  ) : (
    <Text className='me-avatar-ph'>头像</Text>
  )

  return (
    <View className='page me-page'>
      <View className='me-nav'>
        <Text className='me-nav-title'>我的</Text>
      </View>
      <View className='stage me-stage'>
        <View className='me-hero'>
          <View className='me-avatar-wrap'>
            {isWeapp ? (
              <Button
                className='me-avatar-btn'
                plain
                hoverClass='none'
                openType='chooseAvatar'
                onChooseAvatar={(e) => saveAvatar(e.detail.avatarUrl)}
              >
                {avatarInner}
              </Button>
            ) : (
              <View className='me-avatar-btn me-avatar-fallback'>{avatarInner}</View>
            )}
          </View>
          {isWeapp && connected ? (
            <Input
              className='me-name'
              type='nickname'
              placeholder='点这里填昵称'
              maxlength={32}
              value={user?.nickname || ''}
              onBlur={(e) => saveNickname(e.detail.value)}
            />
          ) : (
            <Text className='me-name-text'>{nickname}</Text>
          )}
          <Text className='me-slogan'>每天闯关一点点，进步看得见</Text>
          {!connected ? (
            <Text className='me-status'>还没连上微信，记录暂时空着</Text>
          ) : null}
        </View>

        <View className='card me-stats'>
          <View className='me-stat'>
            <Text className='me-stat-num'>{stats.times}</Text>
            <Text className='me-stat-label'>闯关次数</Text>
          </View>
          <View className='me-stat'>
            <Text className='me-stat-num'>{stats.correct}</Text>
            <Text className='me-stat-label'>答对题数</Text>
          </View>
          <View className='me-stat'>
            <Text className='me-stat-num'>{stats.rate}</Text>
            <Text className='me-stat-label'>平均正确率</Text>
          </View>
        </View>

        <View
          className='card me-menu'
          onClick={() => Taro.navigateTo({ url: '/pages/about/index' })}
        >
          <Text className='me-menu-icon'>题</Text>
          <Text className='me-menu-label'>关于题目</Text>
          <Text className='me-chevron'>›</Text>
        </View>

        <Text className='me-section'>闯关记录</Text>
        <View className='card me-records'>
          {records.length === 0 ? (
            <View className='me-empty-wrap'>
              <Text className='me-empty-title'>还没有打完的关。</Text>
              <Text className='me-empty'>
                {connected ? '打完一关会出现在这里。' : '连上微信之后，打完的关会出现在这里。'}
              </Text>
            </View>
          ) : (
            records.map((item, index) => (
              <View
                key={item.id}
                className={index === 0 ? 'me-record' : 'me-record me-record-line'}
              >
                <View className='me-record-main'>
                  <Text className='me-record-title'>{item.title}</Text>
                  <Text className='me-record-meta'>
                    {item.total} 题 · 正确率 {accuracyText(item.correct, item.total)}
                  </Text>
                </View>
                <View className='me-replay' onClick={() => replay(item)}>
                  <Text className='me-replay-text'>再打</Text>
                </View>
              </View>
            ))
          )}
        </View>
        <Text className='hint'>不要能力雷达和学时竞赛。</Text>
      </View>
      <TabBar active='me' />
    </View>
  )
}
