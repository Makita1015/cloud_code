import Link from 'next/link'
import { createPet } from '@/app/actions'
import PetForm from '@/components/PetForm'

export default function NewPetPage() {
  return (
    <div>
      <div className="mb-6">
        <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">
          ← 一覧に戻る
        </Link>
        <h1 className="text-2xl font-bold text-gray-800 mt-2">新規カルテ登録</h1>
      </div>
      <PetForm action={createPet} />
    </div>
  )
}
