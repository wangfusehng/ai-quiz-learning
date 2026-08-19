import { Text, View } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import { useState } from 'react'
import { fetchMistakes, silentLogin } from '../../api/client'
import { BackButton } from '../../components/Chrome'
import { useAuth } from '../../store/auth'
import type { MistakeItem } from '../../types/user'
import './index.scss'

const isWeapp = process.env.TARO_ENV === 'weapp'

function excerpt(stem: string, max = 28) {
  const compact = stem.replace(/\s+/g, ' ').trim()
  return compact.length > max ? `${compact.slice(0, max)}…` : compact
}

function relativeTime(iso: string) {
  const then = new Date(iso).getTime()
  if (Number.isNaN(then)) return ''
  const diff = Math.max(0, Date.now() - then)
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days === 1) return '昨天'
  if (days < 30) return `${days} 天前`
  const months = Math.floor(days / 30)
  if (months < 12) return `${months} 个月前`
  return `${Math.floor(months / 12)} 年前`
}

export default function MistakesPage() {
  const status = useAuth((s) => s.status)
  const connected = status === 'connected'
  const [items, setItems] = useState<MistakeItem[]>([])

  useDidShow(() => {
    const load = async () => {
      if (!isWeapp) {
        useAuth.getState().setOffline()
        setItems([])
        return
      }
      if (useAuth.getState().status !== 'connected') {
        const ok = await silentLogin()
        if (!ok) {
          setItems([])
          return
        }
      }
      try {
        const data = await fetchMistakes()
        setItems(data.items)
      } catch {
        useAuth.getState().setOffline()
        setItems([])
      }
    }
    load()
  })

  return (
    <View className='page'>
      <View className='nav'>
        <BackButton onClick={() => Taro.navigateBack()} />
        <Text className='nav-title'>错题本</Text>
        <View style={{ width: 40 }} />
      </View>
      <View className='stage'>
        {items.length > 0 ? (
          <View
            className='btn'
            onClick={() => Taro.navigateTo({ url: '/pages/mistakes/practice/index' })}
          >
            <Text className='btn-label'>练习这些错题</Text>
          </View>
        ) : null}
        <View className={`card mistakes-list${items.length > 0 ? ' mistakes-list-follow' : ''}`}>
          {items.length === 0 ? (
            <View className='mistakes-empty'>
              <Text className='mistakes-empty-title'>还没有收入的错题。</Text>
              <Text className='mistakes-empty-hint'>
                {connected
                  ? '打关时没答对的选择题会自动进来。'
                  : '连上微信之后，答错的选择题会出现在这里。'}
              </Text>
            </View>
          ) : (
            items.map((item, index) => (
              <View
                key={item.id}
                className={index === 0 ? 'mistakes-item' : 'mistakes-item mistakes-item-line'}
                onClick={() =>
                  Taro.navigateTo({ url: `/pages/mistakes/detail/index?id=${item.id}` })
                }
              >
                <View className='mistakes-main'>
                  <Text className='mistakes-title'>{item.title}</Text>
                  <Text className='mistakes-stem'>{excerpt(item.stem)}</Text>
                  <Text className='mistakes-meta'>
                    {item.knowledgePoint} · {relativeTime(item.completedAt)}
                  </Text>
                </View>
                <Text className='mistakes-chevron'>›</Text>
              </View>
            ))
          )}
        </View>
      </View>
    </View>
  )
}
