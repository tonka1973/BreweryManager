---
description: Rebuild the BreweryManager executable using PyInstaller
---

To rebuild the executable for testing:

1.  Run the PyInstaller command to clean and build using the spec file.
    // turbo
    ```bash
    python -m PyInstaller --clean BreweryManager.spec
    ```

2.  Notify the user that the build is complete and point them to the `dist/BreweryManager.exe` file.
