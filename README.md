# envault

> A CLI tool to manage and encrypt local `.env` files with team-sharing support via Git-friendly encrypted blobs.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

Initialize envault in your project and set a shared encryption key:

```bash
# Initialize envault in the current directory
envault init

# Encrypt your .env file into a shareable blob
envault lock --file .env --output .env.vault

# Decrypt a vault file back into a .env file
envault unlock --file .env.vault --output .env

# Rotate the encryption key
envault rotate --file .env.vault
```

Commit `.env.vault` to your repository and keep `.env` in `.gitignore`. Team members can decrypt the vault using the shared key stored securely (e.g., in a password manager or secrets service).

```bash
# Example team workflow
git pull
envault unlock --file .env.vault --output .env
```

---

## How It Works

- Encrypts `.env` files using **AES-256-GCM** symmetric encryption.
- Produces a single, portable `.env.vault` blob that is safe to commit to Git.
- Team members share the encryption key out-of-band (e.g., via a secrets manager).
- No external services required — fully offline and self-contained.

---

## Contributing

Pull requests are welcome! Please open an issue first to discuss any major changes.

---

## License

This project is licensed under the [MIT License](LICENSE).