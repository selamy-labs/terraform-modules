# Basic ARC runner scale set

Deploys a GitHub Actions Runner Controller (ARC) runner scale set against the
`selamy-labs` org with scale-to-zero, using the upstream
`gha-runner-scale-set` chart through the canonical module.

```bash
tofu init
tofu plan
```

Requires:
- An ARC controller already installed (`gha-runner-scale-set-controller`).
- The `github-runner-auth` Secret present in the target namespace.
