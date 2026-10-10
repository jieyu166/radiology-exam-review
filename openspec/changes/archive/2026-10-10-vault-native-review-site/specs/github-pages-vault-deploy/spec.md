## ADDED Requirements

### Requirement: Build and validate Pages artifacts on main

The GitHub Actions workflow SHALL run on pushes to `main` that affect vault publication inputs, review website source, compiler source, validation source, or workflow configuration. The workflow SHALL execute inventory, validation, compiler, static website build, and browser smoke tests before deployment.

#### Scenario: Deploy a valid main build

- **WHEN** a push to `main` passes inventory, validation, compiler, static build, and browser smoke tests
- **THEN** the workflow deploys the generated `dist/` artifact to GitHub Pages

### Requirement: Block deployment after a hard publication failure

The workflow SHALL not deploy when inventory, validation, compiler, static build, or browser smoke tests return nonzero. A failed workflow SHALL publish a machine-readable build report containing hard errors, warnings, published counts, excluded counts, and source hashes. The failed run SHALL not replace the last successful GitHub Pages deployment.

#### Scenario: Preserve the previous deployment

- **WHEN** a main push contains a published question with an invalid SR boundary
- **THEN** the workflow records the validation error, skips Pages deployment, and leaves the prior successful Pages version available

### Requirement: Keep generated artifacts outside the authoring workflow

The deployment artifact SHALL be generated inside Actions or an equivalent reproducible build environment. The repository SHALL not require authors to edit or routinely commit `dist/` content in order to publish vault changes.

#### Scenario: Publish a vault-only change

- **WHEN** an author changes only `vault/concepts/brain-abscess.md` and pushes the commit to `main`
- **THEN** Actions rebuilds and deploys the affected publication package without requiring a manually edited generated JSON file
