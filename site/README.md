<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Explains the two seeded manifest.json
     files (task T012), since JSON admits no comment syntax for an AI-Assisted header. -->
# site/

GitHub Pages source for this repository's two consumer-facing channels.

- `manifest.json` -- the **published** channel (`WGC_DATA_CHANNEL=published`).
- `prerelease/manifest.json` -- the **pre-release** channel (`WGC_DATA_CHANNEL=prerelease`),
  consumed by Dev/Test app builds.

Both files are seeded here with an empty `versions[]` array (`rules-data-manifest.md` v1.1.1
§2), so both channels resolve to valid JSON before anything has ever been published. Only
`.github/workflows/publish.yml` and `withdraw.yml` may regenerate these files thereafter
(`contracts/pipeline-run-interface.md` §3-§4); no other code path writes here.
