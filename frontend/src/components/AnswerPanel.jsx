import { useState } from 'react'
import SourceCard from './SourceCard'

function renderAnswerWithCitations(text) {
  const parts = text.split(/(\[\d+\])/g)
  return parts.map((part, i) => {
    const match = part.match(/^\[(\d+)\]$/)
    if (match) {
      return (
        <sup key={i}>
          <span className="inline-flex items-center justify-center min-w-[1.25rem] h-5 rounded bg-blue-100 text-blue-700 text-xs font-bold px-1 mx-0.5">
            {match[1]}
          </span>
        </sup>
      )
    }
    return <span key={i}>{part}</span>
  })
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
        <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
          {renderAnswerWithCitations(result.answer)}
        </p>
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
