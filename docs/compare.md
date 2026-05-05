# envault compare

The `compare` command lets you diff two `.env` files or encrypted vault files side-by-side.

## Commands

### `envault compare env <left> <right>`

Compare two plain `.env` files.

```bash
envault compare env .env.staging .env.production
```

**Options:**

| Flag | Description |
|------|-------------|
| `--mask` | Hide actual values in the diff output (safe for sharing logs) |

**Output legend:**

| Symbol | Meaning |
|--------|---------|
| `<` | Key only in the left file |
| `>` | Key only in the right file |
| `~` | Key exists in both but values differ |

**Exit codes:**
- `0` — files are identical
- `1` — differences were found

---

### `envault compare vault <left> <right>`

Compare two encrypted vault files. Both vaults must share the same password.

```bash
envault compare vault staging.vault production.vault --password mypassword
```

**Options:**

| Flag | Description |
|------|-------------|
| `--password` | Decryption password (prompted if omitted) |
| `--mask` | Hide actual values in the diff output |

---

## Example output

```
Summary: 1 only in left, 1 value(s) changed.
< OLD_KEY
~ DATABASE_URL: 'postgres://localhost/dev' -> 'postgres://prod-host/app'
```

## Use cases

- Auditing differences between environment stages before deployment
- Reviewing what changed between two shared vault exports
- CI checks to ensure staging and production configs stay in sync
