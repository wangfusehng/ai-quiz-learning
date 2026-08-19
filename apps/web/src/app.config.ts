export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/wait/index',
    'pages/quiz/index',
    'pages/fail/index',
    'pages/report/index',
    'pages/records/index',
    'pages/me/index',
    'pages/about/index',
    'pages/mistakes/index',
    'pages/mistakes/detail/index',
    'pages/mistakes/practice/index',
  ],
  window: {
    navigationStyle: 'custom',
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#fff6ef',
    navigationBarTitleText: '关卡学',
    navigationBarTextStyle: 'black',
    backgroundColor: '#fff6ef',
  },
})
