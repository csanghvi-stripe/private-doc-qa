# Desktop App

Tauri + React + TypeScript

## Dev

```bash
npm install
npm run tauri dev
```

## Build

```bash
npm run tauri build
# Output: src-tauri/target/release/bundle/
```

## Structure

```
desktop/
├── src/                # React frontend
│   ├── App.tsx
│   └── components/
├── src-tauri/          # Rust bridge
│   └── src/main.rs
└── package.json
```

## Tauri Commands

- `init_backend` — Start Python backend
- `add_documents` — Index files
- `ask_question` — Query documents
- `remove_document` — Remove from index
- `record_and_transcribe` — Voice input

## Troubleshooting

**Backend not running:** Run `python setup.py` in parent directory first

**Rust errors:** `rustup update`

**Node errors:** `rm -rf node_modules && npm install`
