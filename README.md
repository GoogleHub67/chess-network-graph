# Chess Matchmaking Network Tree 🕸️

A Python network crawler that builds a visual directory map of players and their match histories from the **Chess.com Public API**. Starting from a single seed user, the script uses a Depth-First Search (DFS) graph traversal to discover matchmaking networks down to three degrees of separation, exporting them in a native Windows `tree /f` syntax layout.

## 🚀 Features
* **Multi-Layer Mapping:** Graphically traces Level 1 (Opponents), Level 2 (Opponents' Opponents), and Level 3 connections.
* **Token Bucket Rate Limiter:** Protects the runtime from server rejections and respects Chess.com endpoint rate boundaries.
* **Archive Fall-through:** Dynamic historical fallbacks check active real-time caches if a month index isn't finalized.
* **Visual Directory Generation:** Compiles and outputs structure mapping utilizing custom ASCII line tracking (`├──`, `└──`, `│`).

## 🛠️ Installation & Run

1. Clone the repository down into your environment:
   ```bash
   git clone https://github.com/GoogleHub67/chess-network-graph
   cd chess-network-tree
   ```

2. Install the necessary request packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Update the `user_agent` parameter in the script configuration with a valid email (as mandated by Chess.com's endpoint rules).

4. Run the code panel:
   ```bash
   python chess_tree.py
   ```

## 📊 Sample Visual Layout Output
When executed using `magnuscarlsen` as the root node, the script generates a structured layout saved inside `chess_tree.txt`:

```text
magnuscarlsen
├── artin10862
│   ├── a-fier
│   │   ├── albaricoque2
│   │   ├── arthurkogan
│   │   └── bazar-wokzal
│   └── achuvettan
│       ├── 0817chess
│       └── 217s
└── blitzerh
    ├── 69360420obama
    └── aakash-dalvi7
```

## 📜 License
This project is open-source and available under the MIT License.
