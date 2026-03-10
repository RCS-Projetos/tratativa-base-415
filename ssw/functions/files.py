import os
from .logger import Logger

class Files:
    def __init__(self, download_dir: str = 'Downloads', default_extension:str = '.csv'):
        self.logger = Logger()
        self.download_dir = download_dir
        self.default_extension = default_extension
    
    def get_download_path(self):
        return os.path.join(os.path.expanduser("~"), self.download_dir)
    
    def get_downloaded_file(self):
        return set([os.path.join(self.get_download_path(), f) for f in os.listdir(self.get_download_path()) if f.endswith(self.default_extension)])
    
    def rename_download_file(self, new_name: str):
        os.rename(self.get_download_file(), new_name)
    
    def delete_download_file(self):
        os.remove(self.get_download_file())