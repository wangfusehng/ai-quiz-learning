import { View, Text } from '@tarojs/components'
import { TabBar } from '../../components/TabBar'

export default function MePage() {
  return (
    <View className='page'>
      <View className='nav'>
        <View className='hello'>
          <Text className='hello-small'>你好，</Text>
          <Text className='hello-strong'>同学</Text>
        </View>
      </View>
      <View className='stage'>
        <View className='card hero'>
          <Text className='hero-title'>第一期没有账号。</Text>
          <Text className='hint'>题目与解析由 AI 根据你提供的材料生成，可能不准确。</Text>
        </View>
      </View>
      <TabBar active='me' />
    </View>
  )
}
