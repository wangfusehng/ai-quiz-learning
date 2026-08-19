import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useEffect } from 'react'
import { TabBar } from '../../components/TabBar'
import { Coin } from '../../components/Chrome'
import { useSession } from '../../store/session'

export default function ReportPage() {
  const report = useSession((s) => s.report)
  const quiz = useSession((s) => s.quiz)
  const resetAll = useSession((s) => s.resetAll)

  useEffect(() => {
    if (!report) {
      Taro.redirectTo({ url: '/pages/index/index' })
    }
  }, [report])

  if (!report) {
    return null
  }

  const total = report.scoreHint.total || 1
  const percent = Math.round((report.scoreHint.correct / total) * 100)
  const title = quiz?.source.title || '这一关'

  const again = () => {
    resetAll()
    Taro.redirectTo({ url: '/pages/index/index' })
  }

  const copyShare = async () => {
    const text = `${report.headline}\n${report.oneLiner}\n${report.invite}`
    await Taro.setClipboardData({ data: text })
  }

  return (
    <View className='page'>
      <View className='nav'>
        <View className='hello'>
          <Text className='hello-small'>{title}</Text>
          <Text className='hello-strong'>这一关打完了</Text>
        </View>
        <Coin text={`+${quiz?.meta.estimatedMinutes || 8} min`} />
      </View>
      <View className='stage'>
        <View className='card'>
          <Text className='card-title'>{report.headline}</Text>
          <Text className='hint'>{report.oneLiner}</Text>
          <View className='master'>
            <View
              className='gauge'
              style={{ background: `conic-gradient(#ff7a33 ${percent}%, #f1e7df 0)` }}
            >
              <View className='gauge-inner'>
                <Text className='gauge-strong'>{percent}%</Text>
                <Text>已掌握</Text>
              </View>
            </View>
            <Text className='hint'>
              {report.scoreHint.total} 道选择里答对 {report.scoreHint.correct} 道。
              {report.scoreHint.shortAnswerNote || '短答另计，不打百分制羞辱。'}
            </Text>
          </View>
        </View>
        <View className='card' style={{ marginTop: 12 }}>
          <Text className='card-b'>最该再看一眼的 2 点</Text>
          <View className='improve'>
            {(report.stillFuzzy.length ? report.stillFuzzy : report.pointsBitten)
              .slice(0, 2)
              .map((item) => (
                <View key={item} className='improve-item'>
                  {item}
                </View>
              ))}
          </View>
        </View>
        <View className='card' style={{ marginTop: 12 }}>
          <Text className='card-b'>分享海报</Text>
          <Text className='hint'>{report.invite}</Text>
          <View className='share-box'>海报 / 金句预览</View>
        </View>
        <View className='btn-row' style={{ marginTop: 14 }}>
          <View className='btn' onClick={again}>
            再来一套
          </View>
          <View className='btn btn-ghost' onClick={copyShare}>
            生成海报
          </View>
        </View>
      </View>
      <TabBar active='me' />
    </View>
  )
}
