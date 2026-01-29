class TemplateRegistryBase:
    """Base class that automatically builds template paths for any app."""

    def __init__(self, base_folder):
        self.base_folder = base_folder

    def base_folder_files(self, name: str):
        """Return a file path joined with BASE_FOLDER."""
        return f"{self.base_folder}/{name}"

    def subfolder(self, name: str):
        """Return a subfolder path joined with BASE_FOLDER."""
        return f"{self.base_folder}/{name}"
