import { View, Text, Textarea } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useMemo, useState } from 'react'
import { TabBar } from '../../components/TabBar'
import { Coin, Ring } from '../../components/Chrome'
import { SAMPLE_MATERIAL, useSession } from '../../store/session'

const TOPICS = [
  {
    title: '损失厌恶',
    desc: '确定损失 · 收益不对称 · 提取练习',
    material: SAMPLE_MATERIAL,
  },
  {
    title: '看懂 ≠ 会讲',
    desc: '测验效应 · 主动回忆 · 8 分钟',
    material:
      '看懂是熟悉感，能讲出来才是提取练习。测验效应说明，主动回忆比再看一遍更有助于记住关键概念。看完视频觉得懂了，转头却说不清损失厌恶到底在怕什么。熟悉感会让人误以为已经掌握，直到被提问才发现讲不完整。材料强调真正的难点不是记术语，而是把确定亏掉和确定赚到放在同一笔钱上对比。卡尼曼讲过，人对确定损失的厌恶，常常大过对同等收益的喜欢。同样一笔钱，确定亏掉往往比确定赚到更扎心。',
  },
]

export default function Index() {
  const material = useSession((s) => s.material)
  const setMaterial = useSession((s) => s.setMaterial)
  const beginGenerate = useSession((s) => s.beginGenerate)
  const [alertOn, setAlertOn] = useState(false)
  const count = useMemo(() => material.trim().length, [material])

  const submit = () => {
    if (count < 200) {
      setAlertOn(true)
      return
    }
    setAlertOn(false)
    beginGenerate()
    Taro.navigateTo({ url: '/pages/wait/index' })
  }

  return (
    <View className='page'>
      <View className='nav'>
        <View className='hello'>
          <Text className='hello-small'>你好，</Text>
          <Text className='hello-strong'>同学</Text>
        </View>
        <Coin text='8 分钟' />
      </View>
      <View className='stage'>
        <View className='card hero'>
          <Text className='hero-title'>今天想闯哪一关？</Text>
          <View className='field'>
            <Text className='field-label'>把刚看完的正文贴进来</Text>
            <Textarea
              className='field-area'
              value={material}
              maxlength={20000}
              placeholder='例如：RAG 的基本概念、Prompt 工程……'
              onInput={(e) => setMaterial(e.detail.value)}
            />
            <Text className='counter'>{count} / 建议≥200</Text>
          </View>
          <Text className='hint'>例如：RAG 的基本概念、工作流程、常见问题、Prompt 工程……</Text>
          <View className={alertOn ? 'alert is-on' : 'alert'}>
            <Text>材料太短，出题会空洞。再贴一段正文。</Text>
          </View>
          <View className='btn' onClick={submit}>
            <Text className='btn-label'>开始生成题目 →</Text>
          </View>
        </View>
        <Text className='section-title'>快速主题</Text>
        <View className='topic-grid'>
          {TOPICS.map((topic) => (
            <View
              key={topic.title}
              className='topic'
              onClick={() => {
                setMaterial(topic.material)
                setAlertOn(false)
              }}
            >
              <Text className='topic-b'>{topic.title}</Text>
              <Text className='topic-span'>{topic.desc}</Text>
            </View>
          ))}
        </View>
        <Text className='section-title'>未完成的关卡</Text>
        <View className='progress-item'>
          <Ring percent={60} />
          <View className='grow'>
            <Text className='grow-b'>行为经济学</Text>
            <Text className='grow-span'>还差 3 题</Text>
          </View>
          <View className='ico'>≡</View>
        </View>
        <View className='progress-item'>
          <Ring percent={40} />
          <View className='grow'>
            <Text className='grow-b'>合成数据</Text>
            <Text className='grow-span'>还差 5 题</Text>
          </View>
          <View className='ico'>◇</View>
        </View>
      </View>
      <TabBar active='home' />
    </View>
  )
}
