import { Heading } from '../../components/Heading/index.tsx'
import { useAuth } from '../../modules/auth/context/AuthContext.ts'
import { useCurrentUser } from '../../modules/auth/hooks/useCurrentUser.ts'
import { AppointmentList } from './components/AppointmentList/index.tsx'
import { Header } from './components/Header/index.tsx'
import { ScheduleAppointmentForm } from './components/ScheduleAppointmentForm/index.tsx'
import styles from './Home.module.scss'

export function Home() {
  const { logOut } = useAuth()
  const { data: user } = useCurrentUser()

  return (
    <>
      <Header email={user?.email} onLogOut={logOut} />
      <main className={styles.home}>
        <Heading level={1} className={styles.homeTitle}>
          Veterinary appointments
        </Heading>
        <div className={styles.homeContent}>
          <section className={styles.homePanel} aria-labelledby="schedule-title">
            <Heading level={2} id="schedule-title" className={styles.homeSectionTitle}>
              Schedule an appointment
            </Heading>
            <ScheduleAppointmentForm />
          </section>
          <section className={styles.homeSection} aria-labelledby="upcoming-title">
            <Heading level={2} id="upcoming-title" className={styles.homeSectionTitle}>
              Upcoming
            </Heading>
            <AppointmentList />
          </section>
        </div>
      </main>
    </>
  )
}
