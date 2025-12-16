# Computer Paths Configuration

This file stores the folder paths for each computer that runs the Brewery Manager application.

---

## Known Computers

### 1. Brewery Computer
- **Name:** Brewery
- **Path:** `C:\Users\darre\Desktop\BreweryManager`
- **User:** darre
- **Added:** November 2025

### 2. Home Computer
- **Name:** Home
- **Path:** `C:\Users\Tonk\OneDrive\Desktop\BreweryManager`
- **User:** Tonk
- **Added:** November 2025

### 3. Admin Computer
- **Name:** Admin
- **Path:** `C:\BreweryManager`
- **User:** Shared (all users)
- **Added:** December 2025

---

## Adding a New Computer

If you're setting up the Brewery Manager on a new computer:

### Step 1: Initial Setup
1. Clone or download the repository to your desired location
2. Note the full path to the BreweryManager folder
3. Install Python 3.11+ if not already installed
4. Run `pip install -r requirements.txt`
5. Test with `python main.py`

### Step 2: Add Computer to This File
Add a new entry above with:
- Computer name/identifier
- Full path to BreweryManager folder
- Your username
- Date added

### Step 3: Update Session Branch
When Claude creates a session branch, it will use the correct path for your computer.

---

## Path Format

**Windows:** `C:\Users\[USERNAME]\[...]\BreweryManager`

Make sure to use the FULL absolute path, including drive letter.

---

## Notes

- Each computer can have the project in a different location
- Paths are used in start.md for merge commands
- Keep this file updated when adding new computers
- Paths should point to the root BreweryManager folder (where main.py is)

---

*Last Updated: November 11, 2025*
