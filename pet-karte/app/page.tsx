import Link from 'next/link'
import { supabase } from '@/lib/supabase'
import PetSearch from '@/components/PetSearch'
import type { PetWithOwner } from '@/types/database'

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>
}) {
  const { q } = await searchParams

  let query = supabase
    .from('pets')
    .select('*, owners(*)')
    .order('created_at', { ascending: false })

  if (q) {
    query = query.ilike('name', `%${q}%`)
  }

  const { data: pets, error } = await query

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">カルテ一覧</h1>
        <Link
          href="/pets/new"
          className="bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          + 新規登録
        </Link>
      </div>

      <PetSearch defaultValue={q} />

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          データの読み込みに失敗しました。Supabaseの設定を確認してください。
        </div>
      )}

      {!error && (
        <>
          {pets && pets.length > 0 ? (
            <div className="mt-4 bg-white rounded-xl border border-gray-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-4 py-3 text-gray-600 font-medium">ペット名</th>
                    <th className="text-left px-4 py-3 text-gray-600 font-medium hidden sm:table-cell">犬種</th>
                    <th className="text-left px-4 py-3 text-gray-600 font-medium">オーナー</th>
                    <th className="text-left px-4 py-3 text-gray-600 font-medium hidden md:table-cell">登録日</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {(pets as PetWithOwner[]).map((pet) => (
                    <tr key={pet.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 font-medium text-gray-800">{pet.name}</td>
                      <td className="px-4 py-3 text-gray-600 hidden sm:table-cell">
                        {pet.breed || '—'}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {pet.owners?.name || '—'}
                      </td>
                      <td className="px-4 py-3 text-gray-500 hidden md:table-cell">
                        {new Date(pet.created_at).toLocaleDateString('ja-JP')}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Link
                          href={`/pets/${pet.id}`}
                          className="text-teal-600 hover:text-teal-800 font-medium text-xs"
                        >
                          詳細 →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="mt-8 text-center text-gray-500">
              {q ? `「${q}」に一致するペットが見つかりませんでした。` : 'まだカルテが登録されていません。'}
            </div>
          )}
        </>
      )}
    </div>
  )
}
