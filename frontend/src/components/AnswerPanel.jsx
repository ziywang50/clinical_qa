import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import SourceCard from './SourceCard'

function CitationBadge({ num }) {
  return (
    <sup>
      <span className="inline-flex items-center justify-center min-w-[1.25rem] h-5 rounded bg-blue-100 text-blue-700 text-xs font-bold px-1 mx-0.5">
        {num}
      </span>
    </sup>
  )
}

function processTextNode(text) {
  const parts = text.split(/(\[\d+\])/g)
  if (parts.length === 1) return text
  return parts.map((part, i) => {
    const match = part.match(/^\[(\d+)\]$/)
    if (match) return <CitationBadge key={i} num={match[1]} />
    return part || null
  })
}

function processChildren(children) {
  if (!children) return children
  const arr = Array.isArray(children) ? children : [children]
  return arr.flatMap((child) => {
    if (typeof child === 'string') {
      const processed = processTextNode(child)
      return Array.isArray(processed) ? processed : [processed]
    }
    return [child]
  })
}

const markdownComponents = {
  h1: ({ children }) => (
    <h1 className="text-lg font-bold text-gray-900 mt-5 mb-2 first:mt-0">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-base font-bold text-gray-900 mt-5 mb-2 first:mt-0">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-sm font-semibold text-gray-800 mt-4 mb-1 first:mt-0">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="text-sm text-gray-800 leading-relaxed mb-3 last:mb-0">
      {processChildren(children)}
    </p>
  ),
  ul: ({ children }) => (
    <ul className="list-disc list-outside text-sm text-gray-800 mb-3 space-y-1 pl-5">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal list-outside text-sm text-gray-800 mb-3 space-y-1 pl-5">
      {children}
    </ol>
  ),
  li: ({ children }) => (
    <li className="leading-relaxed">{processChildren(children)}</li>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-gray-900">{processChildren(children)}</strong>
  ),
  em: ({ children }) => (
    <em className="italic text-gray-700">{processChildren(children)}</em>
  ),
  code: ({ children }) => (
    <code className="bg-gray-100 text-gray-800 rounded px-1 py-0.5 text-xs font-mono">
      {children}
    </code>
  ),
  hr: () => <hr className="my-4 border-gray-200" />,
}

export default function AnswerPanel({ result }) {
  const [keywordsOpen, setKeywordsOpen] = useState(false)

  return (
    <div className="space-y-6">
      {/* Answer */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
          Answer
        </h2>
        <div className="text-sm text-gray-800 leading-relaxed">
          <ReactMarkdown components={markdownComponents}>
            {result.answer}
          </ReactMarkdown>
        </div>
      </div>

      {/* Keywords collapsible */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <button
          className="w-full flex items-center justify-between px-5 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
          onClick={() => setKeywordsOpen((o) => !o)}
        >
          <span>Keywords used</span>
          <svg
            className={`w-4 h-4 transition-transform ${keywordsOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        {keywordsOpen && (
          <div className="px-5 pb-4 text-xs text-gray-600 border-t border-gray-100">
            <pre className="whitespace-pre-wrap mt-3 font-mono bg-gray-50 rounded p-3 overflow-auto">
              {JSON.stringify(result.keywords_used, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Sources grid */}
      {result.sources.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Sources ({result.sources.length})
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {result.sources.map((source, i) => (
              <SourceCard key={source.source_id} source={source} index={i + 1} />
            ))}
          </div>
        </div>
      )}

      {/* Latency */}
      <p className="text-xs text-gray-400 text-right">
        Retrieved in {result.latency_ms.toLocaleString()}ms
      </p>
    </div>
  )
}
