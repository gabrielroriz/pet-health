import { useState } from 'react'
import { Button } from '../../components/Button/index.tsx'
import { Heading } from '../../components/Heading/index.tsx'
import { useAuth } from '../../modules/auth/context/AuthContext.ts'
import { useCurrentUser } from '../../modules/auth/hooks/useCurrentUser.ts'
import { AppointmentCalendar } from './components/AppointmentCalendar/index.tsx'
import { AppointmentList } from './components/AppointmentList/index.tsx'
import { Header } from './components/Header/index.tsx'
import { ScheduleAppointmentForm } from './components/ScheduleAppointmentForm/index.tsx'
import styles from './Home.module.scss'

export function Home() {
  const { logOut } = useAuth()
  const { data: user } = useCurrentUser()
  const [view, setView] = useState<'list' | 'calendar'>('list')

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
          <section className={styles.homeSection} aria-labelledby="appointments-title">
            <div className={styles.homeSectionHeader}>
              <Heading level={2} id="appointments-title" className={styles.homeSectionTitle}>
                {view === 'list' ? 'Upcoming' : 'Calendar'}
              </Heading>
              <div className={styles.homeViewToggle} role="group" aria-label="View">
                <Button
                  size="sm"
                  variant={view === 'list' ? 'primary' : 'secondary'}
                  aria-pressed={view === 'list'}
                  onClick={() => setView('list')}
                >
                  List
                </Button>
                <Button
                  size="sm"
                  variant={view === 'calendar' ? 'primary' : 'secondary'}
                  aria-pressed={view === 'calendar'}
                  onClick={() => setView('calendar')}
                >
                  Calendar
                </Button>
              </div>
            </div>
            {view === 'list' ? <AppointmentList /> : <AppointmentCalendar />}
          </section>
        </div>
      </main>
    </>
  )
}
