import { Button } from './components/Button/index.tsx'
import { Heading } from './components/Heading/index.tsx'
import { Text } from './components/Text/index.tsx'

function App() {
  return (
    <main>
      <Heading level={1}>Pet Health</Heading>
      <Text>Design system preview.</Text>
      <Button>Primary</Button>
      <Button variant="accent">Accent</Button>
      <Button variant="secondary">Secondary</Button>
    </main>
  )
}

export default App
