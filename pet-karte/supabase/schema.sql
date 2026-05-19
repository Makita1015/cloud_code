-- オーナーテーブル
create table if not exists owners (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  phone text not null,
  email text,
  address text,
  emergency_contact text,
  -- 将来のマルチテナント対応用
  salon_id uuid,
  created_at timestamptz not null default now()
);

-- ペットテーブル
create table if not exists pets (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references owners(id) on delete cascade,
  name text not null,
  breed text,
  gender text check (gender in ('male', 'female')),
  birth_date date,
  weight numeric(5,2),
  coat_color text,
  coat_type text,
  allergies text,
  medical_notes text,
  -- 将来のマルチテナント対応用
  salon_id uuid,
  created_at timestamptz not null default now()
);

-- インデックス
create index if not exists pets_owner_id_idx on pets(owner_id);
create index if not exists pets_name_idx on pets(name);

-- RLS（開発中は無効）
-- alter table owners enable row level security;
-- alter table pets enable row level security;
