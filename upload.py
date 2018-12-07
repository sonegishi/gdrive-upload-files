from __future__ import print_function
from apiclient import http
from oauth2client import client, tools, file
from googleapiclient.discovery import build
from os import listdir, path
from httplib2 import Http
import time


class AutomaticUpload:
    def __init__(self, scopes):
        # If modifying these scopes, delete the file token.json.
        self.scopes = scopes

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', self.scopes)
            creds = tools.run_flow(flow, store)
        self.drive_service = build('drive', 'v3', http=creds.authorize(Http()))

    def create_folder(self, folder_name, parent_folder_id=None):
        """
        Create a folder in your Google Drive.
        :param folder_name: A name of the folder being created
        :param parent_folder_id: Default: None. If None, the folder being created will be
        at My Drive of your Google Drive. Otherwise, the folder being created will go under
        the parent folder id passed as a parameter.
        :return: an id of the created folder
        """
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if parent_folder_id is not None:
            folder_metadata['parents'] = [parent_folder_id]
        f = self.drive_service.files().create(body=folder_metadata,
                                              fields='id').execute()
        print('{} Folder ID: {}'.format(folder_name, f.get('id')))
        return f.get('id')

    def upload_file(self, file_path, file_name, parent_id=None):
        """
        Create a file in your Google Drive.
        :param file_path: A path of the file being created
        :param file_name: A name of the file being created
        :param parent_id: Default: None. If None, the file being created will be at
        My Drive of your Google Drive. Otherwise, the file being created will go under
        the parent folder id passed as a parameter.
        :return: an id of the created file
        """
        file_metadata = {
            'name': file_name,
            'copyRequiresWriterPermission': True
        }
        if parent_id is not None:
            file_metadata['parents'] = [parent_id]
        media = http.MediaFileUpload(file_path,
                                     resumable=True)
        f = self.drive_service.files().create(body=file_metadata,
                                              media_body=media,
                                              fields='id').execute()
        print('{} File ID: {}'.format(file_name, f.get('id')))
        return f.get('id')

    def upload_whole_directory(self, dir_name, parent_id=None):
        """
        Upload every file and folder in the given directory path to your Google Drive.
        :param dir_name: A local directory which is being uploaded
        :param parent_id: Default: None. If None, the folder being created will be
        at My Drive of your Google Drive. Otherwise, the folder being created will go under
        the parent folder id passed as a parameter.
        :return: Nothing
        """
        for item in listdir(dir_name):
            if item.startswith('.'):
                continue
            else:
                file_path = path.join(dir_name, item)
                if path.isdir(file_path):
                    new_folder_id = self.create_folder(item, parent_id)
                    self.upload_whole_directory(file_path, new_folder_id)
                else:
                    self.upload_file(file_path, item, parent_id)


if __name__ == '__main__':
    start_time = time.time()

    # Set an id of the parent directory
    dir_id = '...'

    # Set a directory name of the directory or folder you want to upload
    uploading_dir_name = '/Users/...'

    # Create an AutomaticUpload instance
    upload = AutomaticUpload('https://www.googleapis.com/auth/drive')

    # Upload the selected folder to Google Drive
    upload.upload_whole_directory(uploading_dir_name, dir_id)

    elapsed_time = time.time() - start_time
    print('Elapsed Time: {} sec'.format(elapsed_time))
