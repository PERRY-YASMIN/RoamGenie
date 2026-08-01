# Common Errors

- **Out-of-date branch:** commit/stash owned work, fetch, then rebase or merge `origin/develop` on the feature branch.
- **Contract mismatch:** stop; compare the frozen contract; open an issue tagging both owners.
- **Missing environment variable:** add its name and safe example to `.env.example`; never add the value.
- **Dependency unavailable:** use documented mock/fixture; do not hide the failure.
- **Test passes alone but not integrated:** reproduce against `develop` and record request, response, logs, and responsible boundary.
- **Ownership conflict:** do not delete either change; ask Yasmin to assign the merge owner.
