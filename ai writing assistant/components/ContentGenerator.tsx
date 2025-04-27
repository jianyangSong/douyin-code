"use client"

import React, { useState } from 'react'
import StyleSelector, { StyleOption } from './StyleSelector'
import ResultDisplay from './ResultDisplay'

const ContentGenerator = () => {
  const [userInput, setUserInput] = useState('')
  const [selectedStyle, setSelectedStyle] = useState<StyleOption>('种草笔记')
  const [generatedContent, setGeneratedContent] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!userInput.trim()) {
      setError('请输入产品或内容描述')
      return
    }
    
    setIsLoading(true)
    setError(null)
    setGeneratedContent('')
    
    let result = ''
    let aborted = false
    
    try {
      console.log('开始请求生成API')
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userInput, selectedStyle }),
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('API响应错误:', response.status, errorText)
        throw new Error(`生成失败 (${response.status})，请稍后再试`)
      }
      
      // 处理流式响应
      if (!response.body) {
        throw new Error('返回数据流为空')
      }
      
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      console.log('开始处理流式响应')
      let bufferStr = '' // 用于处理跨块的不完整数据
      
      while (!aborted) {
        const { done, value } = await reader.read()
        
        if (done) {
          console.log('流读取完成')
          break
        }
        
        // 解码二进制数据
        const chunk = decoder.decode(value, { stream: true })
        console.log('收到数据块:', chunk.length, '字节')
        
        // 将新块添加到缓冲区
        bufferStr += chunk
        
        // 处理完整的SSE行
        const lines = bufferStr.split('\n')
        // 保留最后一行，它可能是不完整的
        bufferStr = lines.pop() || ''
        
        for (const line of lines) {
          if (line.trim() === '' || line.includes('[DONE]')) continue
          
          try {
            // 提取内容部分
            if (line.startsWith('data: ')) {
              const jsonData = line.replace('data: ', '').trim()
              if (jsonData) {
                const parsedData = JSON.parse(jsonData)
                const content = parsedData.choices[0]?.delta?.content || ''
                if (content) {
                  result += content
                  setGeneratedContent(result)
                }
              }
            }
          } catch (err) {
            console.error('解析SSE行失败:', line, err)
          }
        }
      }
      
      // 处理缓冲区中的任何剩余数据
      if (bufferStr.trim() !== '') {
        try {
          if (bufferStr.startsWith('data: ') && !bufferStr.includes('[DONE]')) {
            const jsonData = bufferStr.replace('data: ', '').trim()
            if (jsonData) {
              const parsedData = JSON.parse(jsonData)
              const content = parsedData.choices[0]?.delta?.content || ''
              if (content) {
                result += content
                setGeneratedContent(result)
              }
            }
          }
        } catch (err) {
          console.error('处理剩余缓冲区失败:', bufferStr, err)
        }
      }
      
    } catch (err) {
      console.error('生成过程错误:', err)
      // 如果已经有部分内容生成，告知用户内容可能不完整
      if (result) {
        setError('内容生成中断，显示的结果可能不完整')
      } else {
        setError('生成失败，请稍后再试')
      }
    } finally {
      setIsLoading(false)
      if (aborted) {
        console.log('生成请求被中止')
      } else {
        console.log('生成完成，内容长度:', result.length)
      }
    }
  }
  
  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="userInput" className="block text-lg font-medium mb-2 text-gray-300">
            输入你的产品/种草需求描述
          </label>
          <textarea
            id="userInput"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="例如：一款保湿效果很好的面霜，适合干皮，价格实惠，冬天用不会干..."
            className="w-full h-32 px-4 py-3 bg-gray-800 text-white rounded-xl border border-gray-700 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none"
          />
          {error && <p className="text-red-500 mt-1">{error}</p>}
        </div>
        
        <StyleSelector selectedStyle={selectedStyle} onStyleChange={setSelectedStyle} />
        
        <button 
          type="submit" 
          className="btn btn-primary w-full py-3"
          disabled={isLoading}
        >
          {isLoading ? '生成中...' : '生成小红书文案'}
        </button>
      </form>
      
      {(isLoading || generatedContent) && (
        <div className="mt-8">
          <ResultDisplay content={generatedContent} isLoading={isLoading} />
        </div>
      )}
    </div>
  )
}

export default ContentGenerator 