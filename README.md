# Store apps

Two Capacitor 8 wrappers built by GitHub Actions (`.github/workflows/android.yml`):

- `hinkali/` — guest app «Хинкальная» (`hincaly.city.russia`), opens https://hinkali.chikchak.ai/ with `ChikChakApp` in the User-Agent, so orders go as source MOBILE.
- `chikchak/` — staff app ChikChak (`ai.chikchak.app`), opens https://panel.chikchak.ai/.

Each push to `main` builds a signed `.aab` (Google Play) and `.apk` (direct install) per app; take them from the run's artifacts.
Upload keys are repository secrets `<app>_P12` (base64 PKCS12, alias `upload`) and `<app>_PAROL`.
Icons and splash: `py -X utf8 znachki.py <app> <square.png> <#background> <scale>`.

Хинкальная starts from a local animated splash (`hinkali/www/index.html`, layers in `www/zastavka/` from
`zastavka_sloi.py`), then goes to the storefront. Check it frame by frame: `py -X utf8 kadry_zastavki.py <out.png>`.
