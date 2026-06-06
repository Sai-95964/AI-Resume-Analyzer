# Security

## API keys

- Store secrets only in `.env` on your machine.
- **Never** commit `.env` to git (`.gitignore` excludes it).
- **Never** paste API keys in chat, issues, pull requests, or screenshots.

## If your key was exposed

1. Open [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials).
2. Find the key (e.g. **AI-Resume-Analyzer**) and click **Delete key**.
3. Create a **new** API key.
4. Restrict the new key (HTTP referrers or IP) and enable only **Generative Language API**.
5. Put the new key only in your local `.env` as `GOOGLE_API_KEY`.

## Production

- Set a strong `SECRET_KEY` in `.env`.
- Run with `FLASK_DEBUG=false`.
- Use HTTPS in front of the app (reverse proxy).
- Do not send resumes to third-party APIs unless users consent (LLM calls transmit resume text).
