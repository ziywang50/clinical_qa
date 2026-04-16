export default function SourceCard({ source, index }) {
  const isCT = source.source_type === 'clinicaltrials'

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-xs font-bold shrink-0">
          {index}
        </span>
        <span
          className={`text-xs font-medium px-2 py-0.5 rounded-full ${
            isCT
              ? 'bg-teal-100 text-teal-700'
              : 'bg-orange-100 text-orange-700'
          }`}
        >
          {isCT ? 'ClinicalTrials' : 'PubMed'}
        </span>
      </div>

      <a
        href={source.url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-sm font-semibold text-gray-900 hover:text-blue-600 leading-snug"
      >
        {source.title}
      </a>

      <p className="text-xs text-gray-600 line-clamp-3">{source.summary}</p>

      <span className="text-xs font-mono text-gray-400">{source.source_id}</span>
    </div>
  )
}
