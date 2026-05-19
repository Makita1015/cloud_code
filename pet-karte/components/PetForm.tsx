'use client'

import { useActionState } from 'react'
import type { Pet, Owner } from '@/types/database'

type Props = {
  action: (formData: FormData) => Promise<void>
  pet?: Pet
  owner?: Owner
}

export default function PetForm({ action, pet, owner }: Props) {
  const [error, formAction, isPending] = useActionState(
    async (_prev: string | null, formData: FormData) => {
      try {
        await action(formData)
        return null
      } catch (e) {
        return e instanceof Error ? e.message : '登録に失敗しました'
      }
    },
    null
  )

  return (
    <form action={formAction} className="space-y-6">
      {pet && <input type="hidden" name="owner_id" value={owner?.id} />}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* オーナー情報 */}
      <section className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-700 mb-4">オーナー情報</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              氏名 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="owner_name"
              defaultValue={owner?.name}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              電話番号 <span className="text-red-500">*</span>
            </label>
            <input
              type="tel"
              name="phone"
              defaultValue={owner?.phone}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">メールアドレス</label>
            <input
              type="email"
              name="email"
              defaultValue={owner?.email ?? ''}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">緊急連絡先</label>
            <input
              type="tel"
              name="emergency_contact"
              defaultValue={owner?.emergency_contact ?? ''}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">住所</label>
            <input
              type="text"
              name="address"
              defaultValue={owner?.address ?? ''}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
        </div>
      </section>

      {/* ペット情報 */}
      <section className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-700 mb-4">ペット情報</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              ペット名 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="pet_name"
              defaultValue={pet?.name}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">犬種</label>
            <input
              type="text"
              name="breed"
              defaultValue={pet?.breed ?? ''}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">性別</label>
            <select
              name="gender"
              defaultValue={pet?.gender ?? ''}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
            >
              <option value="">選択してください</option>
              <option value="male">オス</option>
              <option value="female">メス</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">生年月日</label>
            <input
              type="date"
              name="birth_date"
              defaultValue={pet?.birth_date ?? ''}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">体重（kg）</label>
            <input
              type="number"
              name="weight"
              defaultValue={pet?.weight ?? ''}
              step="0.1"
              min="0"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">毛色</label>
            <input
              type="text"
              name="coat_color"
              defaultValue={pet?.coat_color ?? ''}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">毛質</label>
            <input
              type="text"
              name="coat_type"
              defaultValue={pet?.coat_type ?? ''}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">アレルギー</label>
            <textarea
              name="allergies"
              defaultValue={pet?.allergies ?? ''}
              rows={2}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">持病・医療メモ</label>
            <textarea
              name="medical_notes"
              defaultValue={pet?.medical_notes ?? ''}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
            />
          </div>
        </div>
      </section>

      <button
        type="submit"
        disabled={isPending}
        className="w-full bg-teal-600 hover:bg-teal-700 disabled:bg-teal-400 text-white font-medium py-3 rounded-lg transition-colors text-sm"
      >
        {isPending ? '保存中...' : '保存する'}
      </button>
    </form>
  )
}
