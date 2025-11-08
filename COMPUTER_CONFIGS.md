# Computer Configurations

**Reference guide for known computers accessing this project**

---

## Known Computers

### 1. Brewery Computer
- **Location:** Brewery/Work
- **Path:** `C:\Users\darre\Desktop\BreweryManager`
- **Quick ID:** "brewery" or "work"
- **Python:** python
- **Notes:** Main development computer at brewery location

### 2. Home Computer
- **Location:** Home
- **Path:** `C:\Users\Tonk\OneDrive\Desktop\BreweryManager`
- **Quick ID:** "home"
- **Python:** python
- **Notes:** Home workstation with OneDrive sync

---

## Adding a New Computer

If you're accessing from a new computer:

1. Tell Claude the full path to the BreweryManager folder
2. Claude will provide the correct commands using your path
3. Optionally, add the computer to this file for future reference

### Template for New Computer:

```markdown
### 3. [Computer Name]
- **Location:** [Where is it?]
- **Path:** `[Full path to BreweryManager]`
- **Quick ID:** "[short identifier]"
- **Python:** [python/python3/py]
- **Notes:** [Any special notes]
```

---

## Path Verification

If you're unsure of your path, run this in Command Prompt:
```cmd
cd Desktop\BreweryManager
echo %CD%
```

Or if using OneDrive:
```cmd
cd OneDrive\Desktop\BreweryManager
echo %CD%
```

---

*Last Updated: November 8, 2025*
