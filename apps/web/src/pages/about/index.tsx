import { Text, View } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { BackButton } from '../../components/Chrome'

export default function AboutPage() {
  return (
    <View className='page'>
      <View className='nav'>
        <BackButton onClick={() => Taro.navigateBack()} />
        <Text className='nav-title'>关于题目</Text>
        <View style={{ width: 40 }} />
      </View>
      <View className='stage'>
        <View className='card hero'>
          <Text className='hero-title'>AI 生成，有依据才出题。</Text>
          <Text className='hint'>材料由你提供。题目、讲解、报告由模型生成，可能不准确。每题应能指回原句。</Text>
          <Text className='hint'>不是题库、不是家教、不是课程商城。</Text>
        </View>
      </View>
    </View>
  )
}
