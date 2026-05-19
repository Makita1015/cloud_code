'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { supabase } from '@/lib/supabase'

export async function createPet(formData: FormData) {
  const ownerName = formData.get('owner_name') as string
  const phone = formData.get('phone') as string
  const email = (formData.get('email') as string) || null
  const address = (formData.get('address') as string) || null
  const emergencyContact = (formData.get('emergency_contact') as string) || null

  const petName = formData.get('pet_name') as string
  const breed = (formData.get('breed') as string) || null
  const gender = (formData.get('gender') as string) || null
  const birthDate = (formData.get('birth_date') as string) || null
  const weightRaw = formData.get('weight') as string
  const weight = weightRaw ? parseFloat(weightRaw) : null
  const coatColor = (formData.get('coat_color') as string) || null
  const coatType = (formData.get('coat_type') as string) || null
  const allergies = (formData.get('allergies') as string) || null
  const medicalNotes = (formData.get('medical_notes') as string) || null

  if (!ownerName || !phone || !petName) {
    throw new Error('必須項目を入力してください')
  }

  const { data: owner, error: ownerError } = await supabase
    .from('owners')
    .insert({ name: ownerName, phone, email, address, emergency_contact: emergencyContact })
    .select()
    .single()

  if (ownerError || !owner) {
    throw new Error('オーナー情報の登録に失敗しました')
  }

  const { error: petError } = await supabase.from('pets').insert({
    owner_id: owner.id,
    name: petName,
    breed,
    gender: gender as 'male' | 'female' | null,
    birth_date: birthDate,
    weight,
    coat_color: coatColor,
    coat_type: coatType,
    allergies,
    medical_notes: medicalNotes,
  })

  if (petError) {
    await supabase.from('owners').delete().eq('id', owner.id)
    throw new Error('ペット情報の登録に失敗しました')
  }

  revalidatePath('/')
  redirect('/')
}

export async function updatePet(id: string, formData: FormData) {
  const petName = formData.get('pet_name') as string
  const breed = (formData.get('breed') as string) || null
  const gender = (formData.get('gender') as string) || null
  const birthDate = (formData.get('birth_date') as string) || null
  const weightRaw = formData.get('weight') as string
  const weight = weightRaw ? parseFloat(weightRaw) : null
  const coatColor = (formData.get('coat_color') as string) || null
  const coatType = (formData.get('coat_type') as string) || null
  const allergies = (formData.get('allergies') as string) || null
  const medicalNotes = (formData.get('medical_notes') as string) || null

  const ownerName = formData.get('owner_name') as string
  const phone = formData.get('phone') as string
  const email = (formData.get('email') as string) || null
  const address = (formData.get('address') as string) || null
  const emergencyContact = (formData.get('emergency_contact') as string) || null
  const ownerId = formData.get('owner_id') as string

  if (!ownerName || !phone || !petName) {
    throw new Error('必須項目を入力してください')
  }

  const { error: petError } = await supabase
    .from('pets')
    .update({
      name: petName,
      breed,
      gender: gender as 'male' | 'female' | null,
      birth_date: birthDate,
      weight,
      coat_color: coatColor,
      coat_type: coatType,
      allergies,
      medical_notes: medicalNotes,
    })
    .eq('id', id)

  if (petError) throw new Error('ペット情報の更新に失敗しました')

  const { error: ownerError } = await supabase
    .from('owners')
    .update({ name: ownerName, phone, email, address, emergency_contact: emergencyContact })
    .eq('id', ownerId)

  if (ownerError) throw new Error('オーナー情報の更新に失敗しました')

  revalidatePath(`/pets/${id}`)
  revalidatePath('/')
  redirect(`/pets/${id}`)
}

export async function deletePet(id: string, ownerId: string) {
  const { error: petError } = await supabase.from('pets').delete().eq('id', id)
  if (petError) throw new Error('ペット情報の削除に失敗しました')

  const { count } = await supabase
    .from('pets')
    .select('id', { count: 'exact', head: true })
    .eq('owner_id', ownerId)

  if (count === 0) {
    await supabase.from('owners').delete().eq('id', ownerId)
  }

  revalidatePath('/')
  redirect('/')
}
