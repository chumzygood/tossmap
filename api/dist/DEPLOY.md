# tossmap-api deploy artifact

Main module: `index.js`. Compatibility date: `2026-11-25`; flags: `nodejs_compat`. The exact multipart metadata is `metadata.json`: SQLite Durable Object `State` with migration `v1`, rate limits `GENERAL_LIMIT` (namespace 1001, 60/60s) and `CHALLENGE_LIMIT` (namespace 1002, 20/60s), vars `X402_NETWORK` (testnet) and `PAY_TO_ADDRESS` (empty). Set PAY_TO_ADDRESS to the intended recipient in the metadata before uploading. The local dummy address is never included.

Upload `metadata.json` as the metadata part and `index.js` as an ES module part named `index.js` to the Workers Script Upload API for worker `tossmap-api`. Configure the custom domain separately. This artifact has not been uploaded or tested with a real payment.
