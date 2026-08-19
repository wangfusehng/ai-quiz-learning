import { View, Text } from '@tarojs/components'
import { TabBar } from '../../components/TabBar'

export default function RecordsPage() {
  return (
    <View className='page'>
      <View className='nav'>
        <View className='hello'>
          <Text className='hello-small'>记录</Text>
          <Text className='hello-strong'>还没有存档</Text>
        </View>
      </View>
      <View className='stage'>
        <View className='card hero'>
          <Text className='hero-title'>这一期不接学习记录。</Text>
          <Text className='hint'>底部可以点进来看看，关卡数据只在这次打开里。</Text>
        </View>
      </View>
      <TabBar active='records' />
    </View>
  )
}
