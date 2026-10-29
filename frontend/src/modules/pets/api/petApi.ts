import { apiRequest } from '../../auth/api/apiClient.ts'

export type Species = 'dog' | 'cat' | 'bird' | 'rabbit' | 'other'

export interface Pet {
  id: string
  name: string
  species: Species
  birthDate: string | null
  breed: string | null
}

interface PetResponse {
  id: string
  name: string
  species: Species
  birth_date: string | null
  breed: string | null
}

// The logged-in user's pets, sorted by name.
export async function listPets(token: string): Promise<Pet[]> {
  const pets = await apiRequest<PetResponse[]>('/pets', token)
  return pets.map((pet) => ({
    id: pet.id,
    name: pet.name,
    species: pet.species,
    birthDate: pet.birth_date,
    breed: pet.breed,
  }))
}
