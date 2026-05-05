# Envault Tags

The **tags** feature lets you annotate individual environment variable keys with
arbitrary labels (e.g. `production`, `secrets`, `db`). Tags are stored in a
lightweight JSON sidecar file (`.envault_tags.json`) alongside your vault.

## Storage

Tags are persisted in `.envault_tags.json` as a plain JSON mapping:

```json
{
  "DB_HOST": ["db", "production"],
  "API_KEY": ["secrets"]
}
```

This file is human-readable and Git-friendly — commit it alongside your
encrypted vault to share tag metadata with your team.

## CLI Usage

### Add a tag

```bash
envault tags add DB_HOST db
envault tags add DB_HOST production
```

### Remove a tag

```bash
envault tags remove DB_HOST production
```

### List all tags

```bash
envault tags list
# All tags: db, production, secrets
```

### List tags for a specific key

```bash
envault tags list --key DB_HOST
# Tags for 'DB_HOST': db, production
```

### List keys with a specific tag

```bash
envault tags list --tag secrets
# Keys tagged 'secrets': API_KEY
```

## Python API

```python
from envault.tags import add_tag, keys_for_tag, tags_for_key, all_tags

add_tag("API_KEY", "secrets")
add_tag("API_KEY", "prod")

print(tags_for_key("API_KEY"))   # ['secrets', 'prod']
print(keys_for_tag("secrets"))   # ['API_KEY']
print(all_tags())                # ['prod', 'secrets']
```

## Notes

- Tags are **not** encrypted; they only label key names, never values.
- The `--dir` flag can target a different working directory for all commands.
