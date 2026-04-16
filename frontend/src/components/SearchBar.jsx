const EXAMPLES = [
  'What are the latest Phase 3 trials for GLP-1 receptor agonists in type 2 diabetes?',
  'What does recent research say about pembrolizumab in non-small cell lung cancer?',
  'Are there active trials for CAR-T therapy in diffuse large B-cell lymphoma?',
]

export default function SearchBar({ question, setQuestion, onSubmit, loading }) {
  function handleKey(e) {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      onSubmit()
    }
  }

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
        <button
          className="self-end px-5 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-sm font-medium rounded-lg transition-colors"
          onClick={() => onSubmit()}
          disabled={loading || !question.trim()}
        >
          Search
        </button>
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
