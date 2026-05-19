import Link from 'next/link'
import { notFound } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { updatePet, deletePet } from '@/app/actions'
import PetDetailView from '@/components/PetDetailView'
import type { PetWithOwner } from '@/types/database'

export default async function PetDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  const { data: pet, error } = await supabase
    .from('pets')
    .select('*, owners(*)')
    .eq('id', id)
    .single()

  if (error || !pet) {
    notFound()
  }

  const petData = pet as PetWithOwner

  const updateAction = updatePet.bind(null, id)
  const deleteAction = deletePet.bind(null, id, petData.owner_id)

  return (
    <div>
      <div className="mb-6">
        <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">
          ← 一覧に戻る
        </Link>
        <h1 className="text-2xl font-bold text-gray-800 mt-2">{petData.name} のカルテ</h1>
      </div>
      <PetDetailView pet={petData} updateAction={updateAction} deleteAction={deleteAction} />
    </div>
  )
}
