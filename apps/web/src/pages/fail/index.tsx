import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { BackButton } from '../../components/Chrome'

export default function FailPage() {
  return (
    <View className='page'>
      <View className='nav'>
        <BackButton onClick={() => Taro.redirectTo({ url: '/pages/index/index' })} />
        <Text className='nav-title'>没写成</Text>
        <View style={{ width: 40 }} />
      </View>
      <View className='stage'>
        <View className='card hero'>
          <Text className='hero-title'>这页没写成。</Text>
          <Text className='hint'>模型忙，或原句对不上材料。没有用标题瞎编一套题。</Text>
          <View className='btn-row'>
            <View
              className='btn'
              onClick={() => Taro.redirectTo({ url: '/pages/wait/index' })}
            >
              重试
            </View>
            <View
              className='btn btn-ghost'
              onClick={() => Taro.redirectTo({ url: '/pages/index/index' })}
            >
              回首页
            </View>
          </View>
        </View>
      </View>
    </View>
  )
}
