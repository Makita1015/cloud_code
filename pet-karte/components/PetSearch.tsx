'use client'

import { useRouter, usePathname } from 'next/navigation'
import { useTransition } from 'react'

export default function PetSearch({ defaultValue }: { defaultValue?: string }) {
  const router = useRouter()
  const pathname = usePathname()
  const [isPending, startTransition] = useTransition()

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value
    startTransition(() => {
      if (value) {
        router.push(`${pathname}?q=${encodeURIComponent(value)}`)
      } else {
        router.push(pathname)
      }
    })
  }

  return (
    <div className="relative">
      <input
        type="search"
        placeholder="ペット名で検索..."
        defaultValue={defaultValue}
        onChange={handleChange}
        className={`w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent ${isPending ? 'opacity-70' : ''}`}
      />
    </div>
  )
}
