# Optional MCP reference server

This directory contains only the retrieval-server implementation and its package metadata.

The server expects two local artifacts:

- `extracted/`: user-supplied, lawfully held reference texts
- `index.json`: the generated chunk index

Both are intentionally excluded from this repository. To use the server, supply material you are permitted to process and run:

```bash
npm install
node indexer.js
node server.js
```

Do not commit the extracted corpus or generated index.
