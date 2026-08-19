import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'

const TABS = [
  { key: 'home', label: '关卡', url: '/pages/index/index' },
  { key: 'records', label: '记录', url: '/pages/records/index' },
  { key: 'me', label: '我的', url: '/pages/me/index' },
] as const

export function TabBar({ active }: { active: (typeof TABS)[number]['key'] }) {
  return (
    <View className='tabbar'>
      {TABS.map((tab) => (
        <View
          key={tab.key}
          className={active === tab.key ? 'tab is-on' : 'tab'}
          onClick={() => {
            if (tab.url === Taro.getCurrentInstance().router?.path) return
            Taro.redirectTo({ url: tab.url })
          }}
        >
          <Text>{tab.label}</Text>
        </View>
      ))}
    </View>
  )
}
