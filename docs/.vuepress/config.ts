import { defineUserConfig, defaultTheme } from 'vuepress'

export default defineUserConfig({
  head: [['link', { rel: 'icon', href: '/favicon.png' }]],
  locales: {
    // 键名是该语言所属的子路径
    // 作为特例，默认语言可以使用 '/' 作为其路径。
    '/': {
      lang: 'en-US',
      title: 'PyReactivity',
      description: 'Providing a reactivity system similar to Vue.js for Python'
    },
    '/zh/': {
      lang: 'zh-CN',
      title: 'PyReactivity',
      description: '为 Python 提供像 Vue.js 一样的的响应式系统'
    }
  },
  theme: defaultTheme({
    repo: 'https://github.com/frederick-wang/pyreactivity',
    locales: {
      '/': {
        notFound: [
          'It seems you have reached a barren wasteland where no knowledge exists...'
        ],
        selectLanguageText: 'Languages',
        selectLanguageName: 'English',
        editLinkText: 'Edit this page on GitHub',
        navbar: [{ text: 'Documentation', link: '/guide/introduction' }],
        sidebar: {
          '/guide/': [
            {
              text: 'Getting Started',
              children: [
                { text: 'Introduction', link: '/guide/introduction' },
                {
                  text: 'Quick Start',
                  link: '/guide/quick-start'
                }
              ]
            },
            {
              text: 'Essentials',
              children: [
                {
                  text: 'Reactivity Fundamentals',
                  link: '/guide/essentials/reactivity-fundamentals'
                },
                {
                  text: 'Computed Properties',
                  link: '/guide/essentials/computed'
                },
                {
                  text: 'Watchers',
                  link: '/guide/essentials/watchers'
                }
              ]
            }
          ]
        }
      },
      '/zh/': {
        notFound: ['你似乎来到了没有知识存在的荒原...'],
        selectLanguageText: '选择语言',
        selectLanguageName: '简体中文',
        editLinkText: '在 GitHub 上编辑此页',
        navbar: [{ text: '文档', link: '/zh/guide/introduction' }],
        sidebar: {
          '/zh/guide/': [
            {
              text: '开始',
              children: [
                { text: '简介', link: '/zh/guide/introduction' },
                {
                  text: '快速上手',
                  link: '/zh/guide/quick-start'
                }
              ]
            },
            {
              text: '基础',
              children: [
                {
                  text: '响应式基础',
                  link: '/zh/guide/essentials/reactivity-fundamentals'
                },
                {
                  text: '计算属性',
                  link: '/zh/guide/essentials/computed'
                },
                {
                  text: '侦听器',
                  link: '/zh/guide/essentials/watchers'
                }
              ]
            }
          ]
        }
      }
    }
  })
})
