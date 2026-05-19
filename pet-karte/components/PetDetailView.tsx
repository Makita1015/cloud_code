'use client'

import { useState } from 'react'
import PetForm from './PetForm'
import type { PetWithOwner } from '@/types/database'

type Props = {
  pet: PetWithOwner
  updateAction: (formData: FormData) => Promise<void>
  deleteAction: () => Promise<void>
}

const genderLabel: Record<string, string> = {
  male: 'オス',
  female: 'メス',
}

function InfoRow({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div className="py-2 border-b border-gray-100 last:border-0">
      <span className="text-xs text-gray-500 block">{label}</span>
      <span className="text-sm text-gray-800">{value ?? '—'}</span>
    </div>
  )
}

export default function PetDetailView({ pet, updateAction, deleteAction }: Props) {
  const [isEditing, setIsEditing] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  async function handleDelete() {
    setIsDeleting(true)
    try {
      await deleteAction()
    } catch {
      setIsDeleting(false)
      setShowDeleteConfirm(false)
    }
  }

  if (isEditing) {
    return (
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-700">カルテ編集</h2>
          <button
            onClick={() => setIsEditing(false)}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            キャンセル
          </button>
        </div>
        <PetForm action={updateAction} pet={pet} owner={pet.owners} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* アクションボタン */}
      <div className="flex gap-2 justify-end">
        <button
          onClick={() => setIsEditing(true)}
          className="bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          編集
        </button>
        <button
          onClick={() => setShowDeleteConfirm(true)}
          className="bg-white hover:bg-red-50 text-red-600 border border-red-300 text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          削除
        </button>
      </div>

      {/* ペット情報カード */}
      <section className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-700 mb-3">ペット情報</h2>
        <div className="grid grid-cols-2 gap-x-6">
          <InfoRow label="ペット名" value={pet.name} />
          <InfoRow label="犬種" value={pet.breed} />
          <InfoRow label="性別" value={pet.gender ? genderLabel[pet.gender] : null} />
          <InfoRow
            label="生年月日"
            value={pet.birth_date ? new Date(pet.birth_date).toLocaleDateString('ja-JP') : null}
          />
          <InfoRow label="体重" value={pet.weight != null ? `${pet.weight} kg` : null} />
          <InfoRow label="毛色" value={pet.coat_color} />
          <InfoRow label="毛質" value={pet.coat_type} />
          <InfoRow label="アレルギー" value={pet.allergies} />
          <div className="col-span-2">
            <InfoRow label="持病・医療メモ" value={pet.medical_notes} />
          </div>
        </div>
      </section>

      {/* オーナー情報カード */}
      <section className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-700 mb-3">オーナー情報</h2>
        <div className="grid grid-cols-2 gap-x-6">
          <InfoRow label="氏名" value={pet.owners?.name} />
          <InfoRow label="電話番号" value={pet.owners?.phone} />
          <InfoRow label="メールアドレス" value={pet.owners?.email} />
          <InfoRow label="緊急連絡先" value={pet.owners?.emergency_contact} />
          <div className="col-span-2">
            <InfoRow label="住所" value={pet.owners?.address} />
          </div>
        </div>
      </section>

      <div className="text-xs text-gray-400 text-right">
        登録日: {new Date(pet.created_at).toLocaleString('ja-JP')}
      </div>

      {/* 削除確認ダイアログ */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 max-w-sm w-full shadow-xl">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">カルテを削除しますか？</h3>
            <p className="text-sm text-gray-600 mb-6">
              <strong>{pet.name}</strong> のカルテを削除します。この操作は取り消せません。
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                キャンセル
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white py-2 rounded-lg text-sm font-medium transition-colors"
              >
                {isDeleting ? '削除中...' : '削除する'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
