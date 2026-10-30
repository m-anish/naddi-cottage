# Setting up Claude Code with Blender

About 20 minutes, once. You need a paid Claude plan.

## 1. Put this folder somewhere sensible

Unzip `naddi-cottage` into your home folder, for example `/Users/<you>/Projects/naddi-cottage`.

## 2. Open it in Claude Code

1. Open the Claude desktop app and click the **Code** tab.
2. Choose this folder as the project.
3. Claude reads `CLAUDE.md` automatically, so it knows the whole project.

(If you prefer the terminal: `cd ~/Projects/naddi-cottage` and type `claude`.)

## 3. Install Blender

Download Blender from blender.org and drag it into Applications. The scripts were built with Blender 5.2 LTS, so use that or newer.

## 4. Install uv (a small tool the Blender connector needs)

Open Terminal and run:

```bash
brew install uv
```

## 5. Add the Blender connector to Blender

1. Download `addon.py` from the Blender MCP project on GitHub (github.com/ahujasid/blender-mcp).
2. In Blender: **Edit › Preferences › Add-ons**, click the arrow menu › **Install from Disk…**, pick `addon.py`, and tick **Blender MCP**.
3. In the 3D view, press **N** to open the sidebar, go to the **BlenderMCP** tab, and click **Connect to Claude**.

It is a free, open-source, third-party add-on, not made by Anthropic or Blender. It lets Claude run Python inside your open Blender, so save your file before each session.

## 6. Tell Claude Code about the connector

In Terminal, run this once:

```bash
claude mcp add-json "blender" '{"command":"uvx","args":["blender-mcp"]}'
```

Then start a new Claude Code session in this folder.

## 7. First thing to type in Claude Code

> Read CLAUDE.md, then check the Blender connection by adding a test cube to my open Blender and deleting it.

## 8. The Onshape model

In Onshape, right-click the Part Studio or Assembly tab › **Export**, choose **glTF** (and STEP as well, for exact dimensions), and save the files into this folder's `onshape/` folder. Then tell Claude Code it's there.

Later, if you want Claude to read Onshape directly, Onshape gives you API keys in its developer portal; create read-only ones unless you want edits.
