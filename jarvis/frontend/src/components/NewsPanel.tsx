import { useEffect, useState, useCallback } from 'react'
import { Newspaper, RefreshCw, ExternalLink, ChevronDown } from 'lucide-react'

interface NewsItem {
  title: string
  link: string
  source: string
  published: string
  published_ago: string
}

const TOPICS = ['top', 'technology', 'science', 'business', 'health', 'sports', 'world'] as const
type Topic = typeof TOPICS[number]

const TOPIC_LABELS: Record<Topic, string> = {
  top: '🔥 Top',
  technology: '💻 Tech',
  science: '🔬 Science',
  business: '📈 Business',
  health: '❤️ Health',
  sports: '⚽ Sports',
  world: '🌍 World',
}

const API_BASE = 'http://localhost:8000'

export default function NewsPanel() {
  const [items, setItems] = useState<NewsItem[]>([])
  const [topic, setTopic] = useState<Topic>('top')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<string>('')

  const fetchNews = useCallback(async (t: Topic) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/news?topic=${t}&limit=25`)
      if (!res.ok) throw new Error('Failed to fetch')
      const data = await res.json()
      setItems(data.items)
      setLastUpdated(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))
    } catch {
      setError('Could not load news. Check your internet connection.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchNews(topic)
    // Auto-refresh every 5 minutes
    const interval = setInterval(() => fetchNews(topic), 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [topic, fetchNews])

  const handleTopicChange = (t: Topic) => {
    setTopic(t)
  }

  return (
    <div
      data-testid="news-panel"
      className="absolute top-4 left-6 bottom-4 w-[320px] flex flex-col bg-jarvis-card/80 backdrop-blur-sm border border-jarvis-border/40 rounded-2xl shadow-xl overflow-hidden z-10"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-jarvis-border/40 flex-shrink-0">
        <div className="flex items-center gap-2">
          <Newspaper size={15} className="text-jarvis-accent-light" />
          <span className="text-sm font-semibold text-jarvis-text">News</span>
          {lastUpdated && (
            <span className="text-[10px] text-jarvis-muted">· {lastUpdated}</span>
          )}
        </div>
        <button
          onClick={() => fetchNews(topic)}
          disabled={loading}
          className="text-jarvis-muted hover:text-jarvis-text transition-colors disabled:opacity-40"
          aria-label="Refresh news"
          title="Refresh"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* Topic tabs — horizontal scroll */}
      <div className="flex gap-1 px-3 py-2 overflow-x-auto flex-shrink-0 border-b border-jarvis-border/30 scrollbar-hide">
        {TOPICS.map(t => (
          <button
            key={t}
            onClick={() => handleTopicChange(t)}
            className={`flex-shrink-0 px-2.5 py-1 text-[11px] rounded-full transition-colors whitespace-nowrap ${
              topic === t
                ? 'bg-jarvis-accent text-white'
                : 'text-jarvis-muted hover:text-jarvis-text hover:bg-jarvis-surface'
            }`}
          >
            {TOPIC_LABELS[t]}
          </button>
        ))}
      </div>

      {/* News list */}
      <div className="flex-1 overflow-y-auto">
        {error ? (
          <div className="flex flex-col items-center justify-center h-full gap-2 px-4 text-center">
            <p className="text-xs text-jarvis-danger">{error}</p>
            <button
              onClick={() => fetchNews(topic)}
              className="text-xs text-jarvis-accent-light hover:underline"
            >
              Try again
            </button>
          </div>
        ) : loading && items.length === 0 ? (
          <div className="space-y-3 p-3">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="animate-pulse space-y-1.5">
                <div className="h-3 bg-jarvis-border rounded w-full" />
                <div className="h-3 bg-jarvis-border rounded w-4/5" />
                <div className="h-2 bg-jarvis-border/60 rounded w-1/3" />
              </div>
            ))}
          </div>
        ) : (
          <div className="divide-y divide-jarvis-border/20">
            {items.map((item, idx) => (
              <a
                key={idx}
                href={item.link}
                target="_blank"
                rel="noopener noreferrer"
                className="flex flex-col gap-1 px-4 py-3 hover:bg-jarvis-surface/60 transition-colors group"
              >
                <p className="text-xs text-jarvis-text leading-snug line-clamp-3 group-hover:text-white transition-colors">
                  {item.title}
                </p>
                <div className="flex items-center justify-between mt-0.5">
                  <span className="text-[10px] text-jarvis-muted truncate max-w-[180px]">
                    {item.source}
                  </span>
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] text-jarvis-muted">{item.published_ago}</span>
                    <ExternalLink size={9} className="text-jarvis-muted opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>
              </a>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-jarvis-border/30 flex-shrink-0">
        <p className="text-[9px] text-jarvis-muted text-center">
          Powered by Google News RSS · Auto-refreshes every 5 min
        </p>
      </div>
    </div>
  )
}
