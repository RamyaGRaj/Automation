"""
Google Drive Automation Module
Handles authentication, file listing, classification, and movement in Google Drive
"""

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_python_client import discovery
from classifier import classify_document
import tempfile
import io


class GoogleDriveManager:
    """Manages Google Drive operations for file classification and organization"""
    
    # If modifying these scopes, delete the file token.pickle
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        """
        Initialize Google Drive Manager
        
        Args:
            credentials_file: Path to credentials.json from Google Cloud Console
            token_file: Path to save/load OAuth token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print(f"❌ Error: {self.credentials_file} not found")
                    print("Please download credentials from Google Cloud Console")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = discovery.build('drive', 'v3', credentials=creds)
        print("✅ Google Drive authenticated successfully")
        return True
    
    def is_authenticated(self):
        """Check if authenticated with Google Drive"""
        return self.service is not None
    
    def find_folder_by_name(self, folder_name, parent_id='root'):
        """
        Find a folder in Drive by name
        
        Args:
            folder_name: Name of folder to find
            parent_id: Parent folder ID (default: root)
        
        Returns:
            Folder ID or None if not found
        """
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id != 'root':
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            return files[0]['id'] if files else None
        except Exception as e:
            print(f"Error finding folder: {e}")
            return None
    
    def create_folder(self, folder_name, parent_id='root'):
        """
        Create a folder in Google Drive
        
        Args:
            folder_name: Name for new folder
            parent_id: Parent folder ID
        
        Returns:
            Folder ID or None
        """
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id != 'root':
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            print(f"✅ Created folder: {folder_name}")
            return folder['id']
        except Exception as e:
            print(f"Error creating folder: {e}")
            return None
    
    def get_or_create_folder(self, folder_name, parent_id='root'):
        """
        Get folder ID, create if doesn't exist
        
        Args:
            folder_name: Name of folder
            parent_id: Parent folder ID
        
        Returns:
            Folder ID
        """
        folder_id = self.find_folder_by_name(folder_name, parent_id)
        if not folder_id:
            folder_id = self.create_folder(folder_name, parent_id)
        return folder_id
    
    def list_files_in_folder(self, folder_id='root', only_root=True):
        """
        List files in a specific folder
        
        Args:
            folder_id: Folder ID (default: root)
            only_root: Only files directly in this folder (not subfolders)
        
        Returns:
            List of files with id, name, mimeType
        """
        try:
            query = "trashed=false"
            if folder_id != 'root':
                query += f" and '{folder_id}' in parents"
            elif only_root:
                # Only files in root, not in any folder
                query += " and 'root' in parents"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, parents)',
                pageSize=100
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def download_file_content(self, file_id):
        """
        Download file content as bytes
        
        Args:
            file_id: Google Drive file ID
        
        Returns:
            File content as bytes or None
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = request.execute()
            return downloader
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def get_file_metadata(self, file_id):
        """
        Get file metadata
        
        Args:
            file_id: Google Drive file ID
        
        Returns:
            File metadata dict
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, parents'
            ).execute()
            return file
        except Exception as e:
            print(f"Error getting file metadata: {e}")
            return None
    
    def move_file(self, file_id, new_parent_id):
        """
        Move file to a different folder
        
        Args:
            file_id: Google Drive file ID
            new_parent_id: New parent folder ID
        
        Returns:
            Success status
        """
        try:
            # Get current parents
            file = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()
            
            previous_parents = ",".join(file.get('parents', []))
            
            # Move file
            self.service.files().update(
                fileId=file_id,
                addParents=new_parent_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error moving file: {e}")
            return False
    
    def is_file_in_folder(self, file_id, folder_id):
        """
        Check if file is in a specific folder
        
        Args:
            file_id: Google Drive file ID
            folder_id: Google Drive folder ID
        
        Returns:
            True if file is in folder
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()
            
            parents = file.get('parents', [])
            return folder_id in parents
        except Exception as e:
            print(f"Error checking file location: {e}")
            return False


if __name__ == "__main__":
    # Test Google Drive Manager
    print("Testing Google Drive Manager...")
    
    # Check if credentials exist
    if not os.path.exists('credentials.json'):
        print("\n⚠️  credentials.json not found!")
        print("\nTo set up Google Drive automation:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Enable Google Drive API")
        print("4. Create OAuth 2.0 Desktop Application credentials")
        print("5. Download as JSON and save as 'credentials.json'")
        print("6. Run this script again")
    else:
        manager = GoogleDriveManager()
        if manager.is_authenticated():
            print("\n✅ Successfully authenticated with Google Drive")
            
            # List files in root
            files = manager.list_files_in_folder(only_root=True)
            print(f"\nFiles in Drive root: {len(files)}")
            for file in files[:5]:
                print(f"  - {file['name']}")
