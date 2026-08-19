import { Text, View } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'

export default function RecordsPage() {
  useDidShow(() => {
    Taro.redirectTo({ url: '/pages/me/index' })
  })
  return (
    <View className='page'>
      <Text className='hint'>记录已放在「我的」里。</Text>
    </View>
  )
}
