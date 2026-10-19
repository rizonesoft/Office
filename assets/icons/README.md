# Rizonesoft Office icons

Generated icon assets for the suite and its six apps. Every file in this folder (except this README) is produced by `python scripts/build-icons.py` from the design in `scripts/lib/icon_design.py`; do not edit them by hand. The SVG masters the build renders from are in `design/icons/`.

## Regenerate and check

```powershell
python -m pip install -r scripts/requirements.txt
python scripts/build-icons.py          # rebuild and verify every file
python scripts/build-icons.py --check  # fail if a committed file is out of date
```

## Icons

| Key | Name | Counterpart | Linux app id |
| --- | ---- | ----------- | ------------ |
| `rizonesoft-office` | Rizonesoft Office | Microsoft Office | `com.rizonesoft.Office` |
| `write` | Rizonesoft Write | Word | `com.rizonesoft.Write` |
| `grid` | Rizonesoft Grid | Excel | `com.rizonesoft.Grid` |
| `stage` | Rizonesoft Stage | PowerPoint | `com.rizonesoft.Stage` |
| `flow` | Rizonesoft Flow | Visio | `com.rizonesoft.Flow` |
| `plan` | Rizonesoft Plan | Project | `com.rizonesoft.Plan` |
| `mail` | Rizonesoft Mail | Outlook | `com.rizonesoft.Mail` |

The Linux app ids are provisional until `docs/brand/NAMES.md` records the identifier forms (todo/01-brand/TODO-01-suite-naming.md section 3).

## Drawings by size

Each size uses the drawing made for it, not a shrunken large icon.

| Displayed size | Drawing | Apps | Suite |
| -------------- | ------- | ---- | ----- |
| 48 px and up | `lg` | Glass: orb, dark block, frosted pane, symbol | Six-colour orb behind glass |
| 32 to 40 px | `md` | Orb and pane, flat tint, heavy strokes | Same, flat tint |
| 16 to 24 px | `sm` | Orb and pane, solid symbol | Same, flat tint |

On high-density displays the drawing follows the displayed size: the macOS 16 pt @2x slot is the `sm` drawing at 32 pixels.

## Folders

| Folder | Contents |
| ------ | -------- |
| `png/<key>/` | `<key>-<px>.png` at 16, 20, 24, 32, 40, 48, 64, 96, 128, 256, 512 and 1024 |
| `windows/` | `<key>.ico` with 16, 20, 24, 32, 40, 48, 64, 96, 128 and 256 (PNG entries) |
| `macos/` | `<key>.icns` with every slot from 16 to 512 @2x |
| `linux/hicolor/` | Freedesktop theme PNGs (16 to 512) and `scalable/apps/<app id>.svg` |
| `web/` | `favicon.ico` (16, 32, 48), `favicon.svg`, `apple-touch-icon.png` (180, white), `icon-192.png`, `icon-512.png` |
| `palette.json` | Each app's accent and light colour, display name and Linux app id |

## Colours

| App | Light | Accent |
| --- | ----- | ------ |
| Write | `#4f8df7` | `#1e4fc2` |
| Grid | `#34c27a` | `#0f7a45` |
| Stage | `#ff8a4c` | `#d4421b` |
| Flow | `#9b7bf7` | `#5b35c9` |
| Plan | `#2dc2b5` | `#0b7f86` |
| Mail | `#3cc4f0` | `#0b7cc0` |

The colours follow the category convention office suites share (documents blue, spreadsheets green, presentations orange) and are not Microsoft's values. No icon uses a letter, which is what makes Microsoft's icons recognisably theirs.

## Not yet made

Document file-type icons (`.docx`, `.xlsx` and the rest) and the wordmark are still to be designed: todo/01-brand/TODO-02-icon-system.md sections 2 and 5.
