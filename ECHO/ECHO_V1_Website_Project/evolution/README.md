# ECHO Evolution Engine — deployment policy

The V1 Evolution Engine records proposals. The next hosted stage should connect a GitHub App (not a personal access token) with the minimum repository permissions required to create branches and pull requests.

Required release pipeline:
1. An agent creates a branch and pull request; it cannot write to the protected default branch.
2. CI runs unit tests, dependency/security scans, static checks, and integration tests in an isolated environment.
3. A policy classifier labels the change. Security/authentication/permission changes, data migrations, destructive operations, billing changes, and policy changes always require owner approval.
4. Only approved low-risk changes can be auto-merged/deployed under a narrowly scoped GitHub Environment.
5. A deployment health check and smoke test run after release. Failed checks trigger rollback to the last known-good immutable image/release.
6. Every proposal, test result, approval, deployment, and rollback is recorded in an append-only audit trail.

Do not give an AI direct production shell access, unrestricted cloud credentials, the ability to change this policy, or access to secrets in logs. Keep CI and deployment credentials in the host's secret store. This repository does not yet implement the GitHub App, policy classifier, deployment controller, or automatic rollback; those require a selected Git provider and hosting API.
