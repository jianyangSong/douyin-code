# 小红书AI文案生成工具

一个基于Next.js和DeepSeek API的小红书风格文案生成工具，可以快速生成多种风格的小红书文案。

## 功能特点

- 🚀 基于先进的AI模型生成高质量文案
- 🎨 提供四种预设风格：种草笔记、评测体验、日常分享、干货知识
- 💬 流式输出，实时查看生成结果
- 📱 响应式设计，适配各种设备尺寸
- 🌙 现代化深色界面，符合SaaS产品风格

## 技术栈

- **前端框架**: Next.js 14
- **后端**: Next.js API Routes (Edge Functions)
- **AI API**: DeepSeek API
- **样式**: Tailwind CSS
- **部署平台**: Vercel

## 本地开发

1. 克隆仓库
```bash
git clone https://github.com/yourusername/xiaohongshu-ai-copywriter.git
cd xiaohongshu-ai-copywriter
```

2. 安装依赖
```bash
npm install
# 或
yarn
```

3. 创建`.env.local`文件，添加DeepSeek API密钥
```
DEEPSEEK_API_KEY=your_deepseek_api_key
```

4. 启动开发服务器
```bash
npm run dev
# 或
yarn dev
```

5. 打开浏览器访问 [http://localhost:3000](http://localhost:3000)

## 部署到Vercel

1. Fork本仓库到你的GitHub账户
2. 在Vercel上导入项目
3. 在环境变量中添加`DEEPSEEK_API_KEY`
4. 部署!

## 使用指南

1. 在文本框中详细描述你的产品或需求
2. 选择适合的文案风格（种草笔记、评测体验、日常分享、干货知识）
3. 点击"生成小红书文案"按钮
4. 等待AI生成文案结果
5. 使用复制按钮将生成的文案复制到剪贴板

## 许可证

MIT 