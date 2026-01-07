# Brewery Management System - Setup Guide

## 1. Installation
1.  Download `BreweryManager.exe`.
2.  Place it in a folder of your choice (e.g., `Desktop` or `Program Files`).
3.  **Important**: You need a `credentials.json` file for Google integration (see Section 2).

## 2. Google Cloud Setup (One-Time Admin Setup)
To enable Google Sheets syncing, you must create a project in Google Cloud and generate a credentials file.

### Step A: Create Project
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Click **"Select a project"** (top left) > **"New Project"**.
3.  Name it "BreweryManager" and click **Create**.

### Step B: Enable Sheets API
1.  In the Dashboard, search for **"Google Sheets API"** in the top search bar.
2.  Click it and select **ENABLE**.
3.  Do the same for **"Google Drive API"** (optional, but recommended for future features).

### Step C: Configure Consent Screen
1.  Go to **APIs & Services > OAuth consent screen**.
2.  Select **External** (or Internal if you have Google Workspace) and click **Create**.
3.  Fill in the required fields:
    *   **App Name**: Brewery Manager
    *   **User Support Email**: Your email.
    *   **Developer Contact Email**: Your email.
4.  Click **Save and Continue** until finished.
5.  **Important**: Under "Test Users", click **"Add Users"** and add the Gmail addresses of everyone who will use the app (including yourself).

### Step D: Create Credentials
1.  Go to **APIs & Services > Credentials**.
2.  Click **Create Credentials > OAuth client ID**.
3.  **Application Type**: Select **Desktop app**.
4.  Name: "Brewery Desktop Client".
5.  Click **Create**.
6.  A popup will appear. Click the **Download JSON** button (icon with a down arrow).
7.  **Rename** this downloaded file to `credentials.json`.

## 3. First Run
1.  Double-click `BreweryManager.exe`.
2.  The app will detect it is missing credentials and show a "Setup" dialog.
3.  Click the button and select the `credentials.json` file you just created.
4.  The app will import it and launch the dashboard.
5.  On the dashboard, go to **Settings > Integrations** and click **"Connect Account"** to log in with your Google account.

## 4. AI Assistant (Optional)
To use the AI features:
1.  Get an API Key from OpenAI (platform.openai.com) or Google Gemini.
2.  Open the app > **Settings > Integrations**.
3.  Paste the key into the "AI Assistant" section and click **Save**.
