"""
GOOGLE DRIVE SETUP GUIDE
How to get credentials for Google Drive API
"""

SETUP_INSTRUCTIONS = r"""
GOOGLE DRIVE API SETUP - STEP BY STEP GUIDE

STEP 1: Create Google Cloud Project
─────────────────────────────────────
1. Go to: https://console.cloud.google.com/
2. Click "Select a Project" at the top
3. Click "NEW PROJECT"
4. Enter Project name: "Document Automation"
5. Click "CREATE"
6. Wait for project to be created

STEP 2: Enable Google Drive API
─────────────────────────────────────
1. In Cloud Console, search for "Google Drive API" in search bar
2. Click on "Google Drive API"
3. Click "ENABLE"
4. Wait for it to enable

STEP 3: Create OAuth Credentials
─────────────────────────────────────
1. In Cloud Console, go to "Credentials" (left sidebar)
2. Click "CREATE CREDENTIALS"
3. Choose "OAuth client ID"
4. You may be asked to configure OAuth consent screen first:
   a. Click "CONFIGURE CONSENT SCREEN"
   b. Select "External"
   c. Fill in:
      - App name: "Document Automation"
      - User support email: your-email@gmail.com
      - Developer contact: your-email@gmail.com
   d. Click "SAVE AND CONTINUE"
   e. On "Scopes" page, click "SAVE AND CONTINUE"
   f. On "Summary" page, click "BACK TO DASHBOARD"

5. Now back to create OAuth client ID:
   a. Click "CREATE CREDENTIALS" → "OAuth client ID"
   b. Choose "Desktop app"
   c. Click "CREATE"

STEP 4: Download Credentials
─────────────────────────────────────
1. In "OAuth 2.0 Client IDs" section, click the download icon (⬇️)
2. Save the JSON file as "credentials.json"
3. Move "credentials.json" to: c:\Users\ramya\OneDrive\Documents\Automation\

STEP 5: Test Authentication
─────────────────────────────────────
1. Open PowerShell
2. Navigate to: cd c:\Users\ramya\OneDrive\Documents\Automation\
3. Run: python gdrive_manager.py
4. A browser window will open asking for Google Drive access
5. Click "Allow" to authorize
6. The token will be saved for future use

IMPORTANT NOTES:
─────────────────────────────────────
⚠️  SECURITY:
  - credentials.json contains sensitive info
  - NEVER commit to GitHub
  - Add to .gitignore
  - token.pickle is your auth token - also keep private

✅ WHAT THE API CAN DO:
  - Read files and folders in your Google Drive
  - Create folders
  - Move files between folders
  - Read file metadata (name, size, etc.)
  - Does NOT: Delete files, modify file content, share files

📋 QUOTA LIMITS:
  - Free tier: 1,000,000 API calls per day
  - This automation uses ~10-30 calls per run
  - Plenty for testing!

TROUBLESHOOTING:
─────────────────────────────────────
❌ "credentials.json not found"
  → Download credentials from Google Cloud Console

❌ "Failed to authenticate"
  → Delete token.pickle and run again to re-authenticate

❌ "Operation not permitted"
  → Make sure Google Drive API is enabled in Cloud Console

❌ "File not found in Drive"
  → Files must be uploaded to Drive root (not in any folder)

"""

if __name__ == "__main__":
    print(SETUP_INSTRUCTIONS)
