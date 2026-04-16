import { useState, useRef, useEffect } from 'react'

const EXAMPLES = [
  'What are the latest Phase 3 trials for GLP-1 receptor agonists in type 2 diabetes?',
  'What does recent research say about pembrolizumab in non-small cell lung cancer?',
  'Are there active trials for CAR-T therapy in diffuse large B-cell lymphoma?',
]

function GearIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
      />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  )
}

function StopIcon() {
  return (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <rect x="5" y="5" width="14" height="14" rx="2" />
    </svg>
  )
}

export default function SearchBar({
  question,
  setQuestion,
  onSubmit,
  onStop,
  loading,
  maxTokensAnswer,
  setMaxTokensAnswer,
  maxTokensLimitations,
  setMaxTokensLimitations,
}) {
  const [optionsOpen, setOptionsOpen] = useState(false)
  const popoverRef = useRef(null)

  function handleKey(e) {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSearch()
    }
  }

  function handleSearch() {
    setOptionsOpen(false)
    onSubmit()
  }

  // Close popover on outside click
  useEffect(() => {
    if (!optionsOpen) return
    function onMouseDown(e) {
      if (popoverRef.current && !popoverRef.current.contains(e.target)) {
        setOptionsOpen(false)
      }
    }
    document.addEventListener('mousedown', onMouseDown)
    return () => document.removeEventListener('mousedown', onMouseDown)
  }, [optionsOpen])

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <textarea
          className="flex-1 border border-gray-300 rounded-lg px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
          placeholder="Ask a clinical question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKey}
          disabled={loading}
        />

        <div className="self-end flex gap-2">
          {/* Options gear button + popover — hidden while loading */}
          {!loading && (
            <div className="relative" ref={popoverRef}>
              <button
                className={`p-3 border rounded-lg text-gray-500 transition-colors ${
                  optionsOpen
                    ? 'border-blue-400 bg-blue-50 text-blue-600'
                    : 'border-gray-300 hover:bg-gray-50 hover:text-gray-700'
                }`}
                onClick={() => setOptionsOpen((o) => !o)}
                aria-label="Request options"
                aria-expanded={optionsOpen}
              >
                <GearIcon />
              </button>

              {optionsOpen && (
                <div className="absolute right-0 top-full mt-2 w-60 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-10 space-y-4">
                  {/* Max tokens — answer */}
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1.5">
                      Max Tokens (Answer)
                    </label>
                    <input
                      type="number"
                      min={256}
                      max={4096}
                      step={128}
                      value={maxTokensAnswer}
                      onChange={(e) =>
                        setMaxTokensAnswer(Math.min(4096, Math.max(256, Number(e.target.value))))
                      }
                      className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <p className="text-xs text-gray-400 mt-1">256 – 4096</p>
                  </div>

                  {/* Max tokens — limitations */}
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1.5">
                      Max Tokens (Limitations)
                    </label>
                    <input
                      type="number"
                      min={128}
                      max={1024}
                      step={64}
                      value={maxTokensLimitations}
                      onChange={(e) =>
                        setMaxTokensLimitations(
                          Math.min(1024, Math.max(128, Number(e.target.value)))
                        )
                      }
                      className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <p className="text-xs text-gray-400 mt-1">128 – 1024</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Search / Stop button */}
          {loading ? (
            <button
              className="flex items-center gap-2 px-5 py-3 bg-red-500 hover:bg-red-600 text-white text-sm font-medium rounded-lg transition-colors"
              onClick={onStop}
              aria-label="Stop search"
            >
              <StopIcon />
              Stop
            </button>
          ) : (
            <button
              className="px-5 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-sm font-medium rounded-lg transition-colors"
              onClick={handleSearch}
              disabled={!question.trim()}
            >
              Search
            </button>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            className="text-xs bg-white border border-gray-200 hover:border-blue-400 hover:text-blue-600 text-gray-600 rounded-full px-3 py-1 transition-colors"
            onClick={() => {
              setQuestion(ex)
              onSubmit(ex)
            }}
            disabled={loading}
          >
            {ex.length > 60 ? ex.slice(0, 60) + '…' : ex}
          </button>
        ))}
      </div>
    </div>
  )
}
