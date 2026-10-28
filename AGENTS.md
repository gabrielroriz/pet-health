# AGENTS.md

Rules and guidelines for AI agents working in this repository.

## Rules

### Commit

All commit messages must follow Conventional Commits: `<type>[optional scope]: <description>`.

Never credit an AI agent in commits or pull requests: no `Co-Authored-By` trailers, "Generated with" footers, or other agent attribution.

### Module naming (backend)

Name every module so its file name says what it holds, even outside its folder. Use the singular entity name.

- A module that defines one main class is named after that class in snake_case: `Pet` → `pet.py`, `RegisterPet` → `register_pet.py`, `PetRepository` → `pet_repository.py`, `TokenService` → `token_service.py`, `InMemoryPetRepository` → `in_memory_pet_repository.py`.
- A module that groups several items of one kind for an entity or feature is named `<entity>_<kind>.py`: `pet_routes.py`, `pet_schemas.py`, `pet_dependencies.py`, `auth_routes.py`.
- Test files are named `test_<module>.py` after the module they cover, in a folder that mirrors `app/`: `test_in_memory_pet_repository.py`, `test_pet_routes.py`.
- Folders group modules by layer, then by domain or technology: `use_cases/pets/`, `ports/repositories/`, `persistence/in_memory/`.
