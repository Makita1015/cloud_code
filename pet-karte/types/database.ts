export type Owner = {
  id: string
  name: string
  phone: string
  email: string | null
  address: string | null
  emergency_contact: string | null
  salon_id: string | null
  created_at: string
}

export type Pet = {
  id: string
  owner_id: string
  name: string
  breed: string | null
  gender: 'male' | 'female' | null
  birth_date: string | null
  weight: number | null
  coat_color: string | null
  coat_type: string | null
  allergies: string | null
  medical_notes: string | null
  salon_id: string | null
  created_at: string
}

export type PetWithOwner = Pet & {
  owners: Owner
}

export type Database = {
  public: {
    Tables: {
      owners: {
        Row: Owner
        Insert: {
          id?: string
          name: string
          phone: string
          email?: string | null
          address?: string | null
          emergency_contact?: string | null
          salon_id?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          name?: string
          phone?: string
          email?: string | null
          address?: string | null
          emergency_contact?: string | null
          salon_id?: string | null
          created_at?: string
        }
        Relationships: []
      }
      pets: {
        Row: Pet
        Insert: {
          id?: string
          owner_id: string
          name: string
          breed?: string | null
          gender?: 'male' | 'female' | null
          birth_date?: string | null
          weight?: number | null
          coat_color?: string | null
          coat_type?: string | null
          allergies?: string | null
          medical_notes?: string | null
          salon_id?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          owner_id?: string
          name?: string
          breed?: string | null
          gender?: 'male' | 'female' | null
          birth_date?: string | null
          weight?: number | null
          coat_color?: string | null
          coat_type?: string | null
          allergies?: string | null
          medical_notes?: string | null
          salon_id?: string | null
          created_at?: string
        }
        Relationships: [
          {
            foreignKeyName: 'pets_owner_id_fkey'
            columns: ['owner_id']
            referencedRelation: 'owners'
            referencedColumns: ['id']
          }
        ]
      }
    }
    Views: Record<string, never>
    Functions: Record<string, never>
    Enums: Record<string, never>
    CompositeTypes: Record<string, never>
  }
}
