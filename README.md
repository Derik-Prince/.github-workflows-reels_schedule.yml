# Affiliate Reels Automation V2

A from-scratch automation project for product/deal Reels inspired by the uploaded reference Reel's format: presenter-style hook, product visuals, punchy captions, voice-over, dynamic scene changes and a comment keyword CTA.

## What it does

1. Reads products from `config/products.json`.
2. Selects a deal using score + schedule.
3. Creates a **new product-specific script** for Telugu/Hindi/English.
4. Generates voice-over with Edge TTS (free service; see note below).
5. Creates a scene plan based on the product category and available visuals.
6. Renders a 9:16 MP4 with FFmpeg: product shots, Ken Burns motion, captions, price reveal, feature cards, CTA and music/SFX.
7. Optionally publishes the MP4 through Instagram Graph API when `PUBLISH_INSTAGRAM=true` and a public media URL is available.
8. Stores a product-specific keyword so your website/DM layer can resolve the exact product.

## Important reality

The renderer cannot manufacture a real product demonstration video from nothing. For each product you should provide product image/video URLs in `config/products.json`, or connect a future catalog/deal API. The engine then edits those assets automatically.

AI generation is optional. If `GEMINI_API_KEY` is absent, the project uses a deterministic category-aware script engine. If it is present, Gemini is used only for the script/scene plan; rendering remains local with FFmpeg.

## Folder layout

- `config/products.json` — products, prices, affiliate links and visual assets.
- `app/main.py` — complete pipeline.
- `app/script_engine.py` — AI + fallback script generation.
- `app/voice.py` — Telugu/Hindi/English TTS.
- `app/render.py` — dynamic Reel renderer.
- `app/instagram.py` — Instagram publishing adapter.
- `.github/workflows/reels.yml` — 07:00 / 13:00 / 17:00 IST automation.
- `public/` — temporary generated media; do not commit generated MP4s.

## Local setup

Requires Python 3.11+ and FFmpeg.

```bash
python -m pip install -r requirements.txt
python -m app.main --language te
```

For Hindi/English:

```bash
python -m app.main --language hi
python -m app.main --language en
```

## Environment variables

Copy `.env.example` to `.env` for local testing.

- `GEMINI_API_KEY` — optional.
- `PUBLIC_BASE_URL` — public HTTPS base URL that serves generated MP4s before Instagram fetches them.
- `PUBLISH_INSTAGRAM` — `true` or `false`.
- `IG_USER_ID` — Instagram professional account ID.
- `IG_ACCESS_TOKEN` — Meta access token.
- `IG_API_VERSION` — e.g. `v24.0`; use the version currently supported by your Meta app.

## GitHub Actions

Add the same values as GitHub Actions Secrets. The workflow runs at:

- 07:00 IST Telugu
- 13:00 IST Hindi
- 17:00 IST English

The workflow uses UTC cron internally.

### Public media hosting

Instagram's API needs a public HTTPS `video_url`. Set `PUBLIC_BASE_URL` to your Firebase Hosting site (or another public host) and configure that host to serve the generated `public/reels/*.mp4` files. A production deployment should use object storage/CDN with automatic cleanup.

The included workflow does **not** silently claim that GitHub artifacts are public Instagram media URLs. You must configure a real public host.

## Instagram publishing

The adapter creates an Instagram Reel container and then publishes it. The Meta app/token must have the permissions and account eligibility required by the current Instagram API. Test publishing with `PUBLISH_INSTAGRAM=false` first.

## Comment keyword / website routing

Every product has a unique `keyword` and `website_url`. The renderer displays the keyword in the CTA. `config/products.json` is the source of truth for a later comment/webhook service.

Example:

`WATCH` -> `https://yourwebsite.com/p/firebolt-watch`

A future webhook can map the comment keyword back to the exact product and then use your permitted Instagram messaging/comment workflow.

## Reference style

The uploaded reference Reel was used as a **style target**, not as a source of copyrighted footage. The renderer targets its general structure: presenter/hook feel, product-focused cuts, white/black caption cards, fast visual changes and a final comment-for-link CTA. Your own product/person assets should be supplied in the catalog.

## Free-cost expectations

Python, FFmpeg and this code are free. GitHub Actions can be free within applicable limits (especially for public repositories). TTS and AI APIs can have quotas/terms. Instagram API access is subject to Meta's current permissions and limits. This is therefore a **₹0-start architecture**, not an unlimited-free guarantee.
