# Private Doc Q&A - Desktop App

Native macOS app built with Tauri + React + TypeScript.

## Prerequisites

- **Rust**: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- **Node.js 18+**: `brew install node`
- **Python backend**: Set up from parent directory first

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run tauri dev
```

This will:
1. Start the Vite dev server (React frontend)
2. Build and run the Tauri app
3. Connect to the Python backend

## Build for Production

```bash
# Build the app
npm run tauri build
```

The built app will be in:
- `src-tauri/target/release/bundle/dmg/` - DMG installer
- `src-tauri/target/release/bundle/macos/` - .app bundle

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Tauri App                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   React UI   │◄──►│  Tauri/Rust  │◄──►│   Python     │  │
│  │  (Frontend)  │IPC │   (Bridge)   │JSON│  (Backend)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  src/                src-tauri/          ../backend_server.py│
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
desktop/
├── src/                    # React frontend
│   ├── App.tsx            # Main component
│   ├── components/        # UI components
│   │   ├── Header.tsx
│   │   ├── DocumentList.tsx
│   │   ├── DropZone.tsx
│   │   ├── ChatArea.tsx
│   │   ├── InputArea.tsx
│   │   └── StatusBar.tsx
│   ├── hooks/             # Custom React hooks
│   └── lib/               # Utilities
│
├── src-tauri/             # Rust backend
│   ├── src/main.rs        # Tauri commands
│   ├── Cargo.toml         # Rust dependencies
│   └── tauri.conf.json    # Tauri config
│
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Tauri Commands

The Rust backend exposes these commands to the React frontend:

| Command | Description |
|---------|-------------|
| `init_backend` | Initialize Python backend |
| `add_documents` | Index new documents |
| `ask_question` | Query documents |
| `remove_document` | Remove from index |
| `record_and_transcribe` | Voice input |

## Styling

Uses Tailwind CSS with:
- Dark mode support (follows system preference)
- Custom color palette
- macOS-native appearance
- Markdown rendering for AI responses (react-markdown + @tailwindcss/typography)
- Collapsible source citations

## Troubleshooting

### "Backend not running"
Ensure Python and all dependencies are installed in the parent directory:
```bash
cd ..
python setup.py
```

### "Rust compilation errors"
Update Rust:
```bash
rustup update
```

### "Node module errors"
Clear and reinstall:
```bash
rm -rf node_modules
npm install
```
