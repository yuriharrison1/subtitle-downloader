# Developer Guide

## Project Structure

```
subtitle-downloader/
├── src/subtitle_downloader/    # Python package
├── bin/                        # Executable wrappers
├── share/file-manager/         # File manager integrations
├── scripts/                    # Installation scripts
├── tests/                      # Test suite
└── docs/                       # Documentation
```

## Adding New File Managers

1. Add detection in `scripts/install.sh`
2. Create integration in `src/subtitle_downloader/file_managers.py`
3. Add uninstallation in `scripts/uninstall.sh`
