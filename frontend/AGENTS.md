# AGENTS.md — frontend

Rules for working in the frontend. The repository-wide rules in [../AGENTS.md](../AGENTS.md) also apply.

## Rules

### Project structure

```
src/
├── app/            # app-wide setup: route table (App.tsx), query client
├── components/     # design system
├── modules/        # one folder per domain (auth, pets, ...)
│   └── auth/
│       ├── api/        # HTTP calls to the backend
│       ├── context/    # React context and its provider
│       ├── hooks/      # TanStack Query hooks and other domain hooks
│       └── routes/     # route guards
├── pages/          # one folder per screen, composed from modules and components
├── styles/         # tokens and global styles
└── main.tsx        # entry point: providers and router
```

- Put domain logic (API calls, queries, mutations, state) in its module, never in `app/` or at the root of `src/`. A module creates only the subfolders it needs.
- Server data goes through TanStack Query: an `api/` function that calls the backend, wrapped by a `useQuery` or `useMutation` hook in `hooks/`. React context holds client-only state, such as the session token.
- Pages use modules; modules must not import from `pages/`.

### Component scope is set by location

Where a component lives determines who may use it.

- `src/components/` holds the design system: generic components built on the project visual identity. Any part of the app may import them.
- A component inside a feature or page folder (for example `src/pages/Home/components/`) belongs to that feature only. Code outside that folder must not import it. If it becomes needed elsewhere, make it generic and move it up to `src/components/`.
- Design system components must not import from feature or page folders.

### Component folder structure

Each component is a folder named after it (PascalCase) with these files:

```
Button/
├── Button.component.tsx     # the component
├── Button.types.ts          # props and related types
├── Button.module.scss       # styles, as a CSS module
├── Button.test.tsx          # tests
└── index.tsx                # barrel export
```

- The stylesheet must be a CSS module named `<Component>.module.scss`.
- `index.tsx` re-exports the component and its public types. Import components through it, never from the inner files:

  ```tsx
  import { Button } from './components/Button/index.tsx'
  ```

### Styling

- Use the design tokens in [src/styles/tokens.scss](src/styles/tokens.scss) (CSS custom properties such as `var(--color-primary)` and `var(--space-4)`). Do not hard-code colours, font sizes, spacing or radii in components.
- Class names are camelCase. Name modifiers after their block by nesting with `&` (`&Primary` inside `.button` compiles to `.buttonPrimary`), and read them as `styles.buttonPrimary`.
- Global styles live only in [src/styles/global.scss](src/styles/global.scss).

## Visual identity

The design tokens define:

- **Colours:** navy `#13294b` (primary), lime green `#9bbe26` (accent), cyan `#00b1d4` (highlight), teal `#006783` (links), mint `#e4f2e1` and slate `#e2e8f1` (surfaces), grey `#333333` (body text).
- **Typography:** Open Sans for body text. Brandon Grotesque for headings; it is a licensed font and is not bundled yet, so headings fall back to Open Sans.
- **Shape:** pill-shaped buttons.
- **Accessibility:** text on the green accent is navy, not white, because white on that green fails WCAG AA contrast.
