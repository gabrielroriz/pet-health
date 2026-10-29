import { useHospitals } from '../../hospitals/hooks/useHospitals.ts'
import { usePets } from '../../pets/hooks/usePets.ts'
import { useVeterinarians } from '../../veterinarians/hooks/useVeterinarians.ts'
import type { Appointment } from '../api/appointmentApi.ts'

export interface AppointmentLabels {
  petName: string
  veterinarianName: string
  hospitalName: string
}

// Shown until the names arrive.
const LOADING = '…'

// Appointments carry only ids; this looks their names up in the cached lists.
export function useAppointmentLabels(): (appointment: Appointment) => AppointmentLabels {
  const { data: pets } = usePets()
  const { data: veterinarians } = useVeterinarians()
  const { data: hospitals } = useHospitals()

  return (appointment) => ({
    petName: pets?.find((pet) => pet.id === appointment.petId)?.name ?? LOADING,
    veterinarianName:
      veterinarians?.find((vet) => vet.id === appointment.veterinarianId)?.name ?? LOADING,
    hospitalName:
      hospitals?.find((hospital) => hospital.id === appointment.hospitalId)?.name ?? LOADING,
  })
}
