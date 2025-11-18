import { faqs } from '../data/faq'

type FaqListProps = {
    query: string
}

export function FaqList({ query }: FaqListProps) {
    const q = query.trim().toLowerCase()
    const filtered = faqs.filter((f) => {
        if (!q) return true
        return (
            f.question.toLowerCase().includes(q) ||
            f.answer.toLowerCase().includes(q) ||
            f.id.toLowerCase().includes(q)
        )
    })

    return (
        <div className='space-y-3'>
            {filtered.map((f) => (
                <details
                    key={f.id}
                    className='group rounded-md border p-4 open:shadow-sm open:bg-accent/40 transition-colors'
                >
                    <summary className='cursor-pointer font-medium leading-relaxed'>
                        {f.question}
                    </summary>
                    <div className='mt-2 text-sm text-muted-foreground leading-relaxed'>
                        {f.answer}
                    </div>
                </details>
            ))}
            {filtered.length === 0 && (
                <p className='text-sm text-muted-foreground'>未找到匹配的问题。</p>
            )}
        </div>
    )
}

