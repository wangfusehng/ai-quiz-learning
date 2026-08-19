import { View, Text } from '@tarojs/components'

export function Coin({ text }: { text: string }) {
  return (
    <View className='coin'>
      <View className='star'>★</View>
      <Text>{text}</Text>
    </View>
  )
}

export function BackButton({ onClick }: { onClick: () => void }) {
  return (
    <View className='back' onClick={onClick}>
      <Text>‹</Text>
    </View>
  )
}

export function Ring({ percent }: { percent: number }) {
  const p = Math.max(0, Math.min(100, percent))
  return (
    <View
      className='ring'
      style={{ background: `conic-gradient(#ff7a33 ${p}%, #f1e7df 0)` }}
    >
      <View className='ring-inner'>{p}%</View>
    </View>
  )
}
