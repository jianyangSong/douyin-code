import { NextRequest } from 'next/server'

export const runtime = 'edge' // 确保使用Edge运行时

// 风格描述映射
const styleDescriptions = {
  '种草笔记': '充满惊喜感和发现感，多使用"OMG"、"居然"、"神器"等词汇，突出产品的独特卖点',
  '评测体验': '客观评价，包含多角度分析，使用"真实体验"、"深度测评"等可信表达，包含优缺点对比',
  '日常分享': '轻松自然的语调，将产品融入日常生活场景，真实感强，像朋友间的分享',
  '干货知识': '专业性强，内容充实，包含数据、原理或使用技巧，强调实用价值和专业观点'
}

export async function POST(req: NextRequest) {
  const requestId = Math.random().toString(36).substring(2, 15)
  console.log(`[${requestId}] 收到生成请求`)
  
  try {
    const { userInput, selectedStyle } = await req.json()
    
    console.log(`[${requestId}] 请求参数:`, { 
      userInputLength: userInput?.length, 
      selectedStyle 
    })
    
    if (!userInput || !selectedStyle) {
      console.error(`[${requestId}] 参数错误: 缺少必要参数`)
      return new Response(
        JSON.stringify({ error: '缺少必要参数' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      )
    }
    
    // 构建提示词
    const prompt = `
你是一位专业的小红书文案撰写专家，请根据以下信息生成一篇引人入胜的小红书文案：

产品/服务信息：${userInput}

风格要求：${styleDescriptions[selectedStyle as keyof typeof styleDescriptions]}

请确保文案：
1. 开头吸引人，设置悬念或直接点题
2. 使用emoji表情增加活泼感
3. 分段清晰，易于阅读
4. 适当使用小红书平台流行语
5. 结尾有号召性用语
`
    
    console.log(`[${requestId}] 发送请求到DeepSeek API`)
    // 创建并发送到DeepSeek API的请求
    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.DEEPSEEK_API_KEY || ''}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7,
        max_tokens: 1000,
        stream: true,
      }),
    })
    
    if (!response.ok) {
      const error = await response.text()
      console.error(`[${requestId}] DeepSeek API错误:`, response.status, error)
      return new Response(
        JSON.stringify({ 
          error: 'AI服务异常，请稍后再试', 
          details: `状态码: ${response.status}` 
        }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      )
    }
    
    console.log(`[${requestId}] DeepSeek API响应成功，开始流式传输`)
    
    // 确保响应体存在
    if (!response.body) {
      console.error(`[${requestId}] DeepSeek API返回的响应体为空`)
      return new Response(
        JSON.stringify({ error: 'API返回空响应' }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      )
    }
    
    // 直接转发原始响应流，避免自定义处理可能导致的数据丢失
    const transformedResponse = new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Request-ID': requestId
      }
    })
    
    console.log(`[${requestId}] 流式响应已开始`)
    return transformedResponse
    
  } catch (error) {
    console.error(`[${requestId}] 处理错误:`, error)
    return new Response(
      JSON.stringify({ 
        error: '服务异常，请稍后再试',
        details: error instanceof Error ? error.message : '未知错误'
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
} 