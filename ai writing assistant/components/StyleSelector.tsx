import React from 'react'

export type StyleOption = '种草笔记' | '评测体验' | '日常分享' | '干货知识'

interface StyleSelectorProps {
  selectedStyle: StyleOption
  onStyleChange: (style: StyleOption) => void
}

const StyleSelector: React.FC<StyleSelectorProps> = ({ selectedStyle, onStyleChange }) => {
  const styles: StyleOption[] = ['种草笔记', '评测体验', '日常分享', '干货知识']
  
  return (
    <div className="mb-6">
      <h3 className="text-lg font-medium mb-3 text-gray-300">选择文案风格</h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {styles.map((style) => (
          <button
            key={style}
            onClick={() => onStyleChange(style)}
            className={`btn ${
              selectedStyle === style 
                ? 'btn-primary' 
                : 'btn-outline'
            }`}
          >
            {style}
          </button>
        ))}
      </div>
    </div>
  )
}

export default StyleSelector 