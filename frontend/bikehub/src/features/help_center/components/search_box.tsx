type SearchBoxProps = {
    value: string
    onChange: (val: string) => void
}

export function SearchBox({ value, onChange }: SearchBoxProps) {
    return (
        <div className='w-full'>
            <input
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder='搜索问题...'
                className='w-full rounded-md border px-3 py-2 text-sm outline-none ring-0 focus:border-primary'
                aria-label='搜索FAQ'
            />
        </div>
    )
}

