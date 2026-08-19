import { PropsWithChildren } from 'react'
import { useLaunch } from '@tarojs/taro'

import { silentLogin } from './api/client'
import './app.scss'

function App({ children }: PropsWithChildren<any>) {
  useLaunch(() => {
    silentLogin()
  })

  return children
}

export default App
