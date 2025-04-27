import ContentGenerator from '@/components/ContentGenerator'

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center p-4 sm:p-8">
      <div className="w-full max-w-3xl">
        {/* 标题部分 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary mb-2">小红书AI文案生成工具</h1>
          <p className="text-gray-400">基于AI的小红书文案生成助手，让你轻松创建多风格文案</p>
        </div>
        
        {/* 内容生成器组件 */}
        <ContentGenerator />
        
        {/* 页脚 */}
        <footer className="mt-16 text-center text-gray-500 text-sm">
          <p>© 2025 小红书AI文案生成工具 - 由Next.js和DeepSeek API提供技术支持</p>
        </footer>
      </div>
    </main>
  )
} 