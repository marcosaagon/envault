# `envault filter` — Key Filtering

The `filter` command group lets you extract a subset of keys from a `.env` file
or encrypted vault based on prefix, suffix, glob pattern, or regular expression.

## Commands

### `envault filter env`

Filter keys from a plaintext `.env` file.

```bash
envault filter env .env --prefix DB_
envault filter env .env --suffix _KEY
envault filter env .env --pattern "APP_*"
envault filter env .env --regex "^(DB|AWS)_"
envault filter env .env --prefix DB_ --invert
```

### `envault filter vault`

Filter keys from an encrypted vault file.

```bash
envault filter vault .env.vault --password mypassword --prefix DB_
envault filter vault .env.vault --password mypassword --pattern "APP_*"
```

## Options

| Option | Description |
|---|---|
| `--prefix TEXT` | Keep only keys that start with this string |
| `--suffix TEXT` | Keep only keys that end with this string |
| `--pattern TEXT` | Keep only keys matching this glob pattern |
| `--regex TEXT` | Keep only keys matching this regular expression |
| `--invert` | Invert the filter — keep keys that do **not** match |

Multiple options can be combined; all must match for a key to be included.

## Output

Filtered output is written to **stdout** so it can be piped or redirected:

```bash
envault filter env .env --prefix DB_ > db.env
```

A summary line is printed to **stderr**:

```
# Matched 3 of 10 keys.
```

The command exits with code `1` if no keys matched the filter.

## Examples

Extract all AWS-related keys from a vault:

```bash
envault filter vault .env.vault --password "$VAULT_PASS" --prefix AWS_ > aws.env
```

Remove all test keys (keys ending with `_TEST`) from a file:

```bash
envault filter env .env --suffix _TEST --invert > clean.env
```
