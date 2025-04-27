"use client"

import React from 'react'
import { FiCopy, FiCheckCircle } from 'react-icons/fi'

interface ResultDisplayProps {
  content: string
  isLoading: boolean
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ content, isLoading }) => {
  const [copied, setCopied] = React.useState(false)
  const resultRef = React.useRef<HTMLDivElement>(null)
  
  // 自动滚动到最新内容
  React.useEffect(() => {
    if (resultRef.current && content) {
      resultRef.current.scrollTop = resultRef.current.scrollHeight
    }
  }, [content])
  
  const handleCopy = () => {
    if (!content) return
    
    navigator.clipboard.writeText(content)
    setCopied(true)
    
    setTimeout(() => {
      setCopied(false)
    }, 2000)
  }
  
  if (isLoading && !content) {
    return (
      <div className="card animate-pulse">
        <div className="h-4 bg-gray-700 rounded w-3/4 mb-4"></div>
        <div className="h-4 bg-gray-700 rounded w-full mb-4"></div>
        <div className="h-4 bg-gray-700 rounded w-5/6 mb-4"></div>
        <div className="h-4 bg-gray-700 rounded w-4/5"></div>
      </div>
    )
  }
  
  if (!content && !isLoading) {
    return null
  }
  
  return (
    <div className="card relative">
      <button 
        onClick={handleCopy}
        className="absolute top-2 right-2 p-2 text-gray-400 hover:text-primary transition-colors"
        title="复制文案"
      >
        {copied ? <FiCheckCircle className="text-green-500" /> : <FiCopy />}
      </button>
      
      <h3 className="text-lg font-medium mb-4 text-primary">
        {isLoading ? '正在生成小红书文案...' : '生成的小红书文案'}
      </h3>
      
      <div 
        ref={resultRef}
        className="whitespace-pre-line text-gray-200 max-h-96 overflow-y-auto"
      >
        {content}
        {isLoading && (
          <span className="inline-block ml-1 animate-pulse">▌</span>
        )}
      </div>
    </div>
  )
}

export default ResultDisplay 