# MusicBot Pro - Setup & Troubleshooting

## ✅ Build Fixed!
The "Playwright Sync API" error has been resolved by fixing how the browser is managed. The confusion with multiple `dist` folders is also fixed.

## 🚀 How to Run
1. Navigate to the `MusicBot/dist` folder.
   - **Do NOT** use `MusicBot/execution/dist` (it has been removed).
2. Double-click **MusicBot.app** (or run `./MusicBot` in terminal).

This version includes:
- **Style Column**: View music styles directly in the dashboard.
- **Split Art Generation**: "Art Prompts" and "Art Images" are separate steps for better control.
- **Startup Delay**: Configurable in Settings to prevent API limits.

## ⚠️ If App Fails to Open
If macOS blocks the app or it crashes immediately:
1. Open Terminal in `MusicBot/execution`.
2. Run directly from source:
   ```bash
   python3 gui_launcher.py
   ```
   (This runs the same code but bypasses packaging issues).

Enjoy! 🎵
