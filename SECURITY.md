Security notes

- Do not commit `SERVICE_ACCOUNT_JSON` or any credentials.
- Use least-privilege service account for Firestore access.
- Encrypt exported backups if they contain sensitive content.
- For mobile, use Firebase Auth and avoid embedding service account keys.
