from pathlib import Path


class FileSystemTool:

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()

        # 200 KB pro Datei
        self.max_file_size = 200 * 1024

    def _safe_path(self, path: str) -> Path:

        #Converts a relative path into an absolute path
        target = (self.project_root / path).resolve()

        # makes sure it stays inside project_root.
        try:
            target.relative_to(self.project_root)
        except ValueError:
            raise PermissionError(
                "Access outside the project directory is not allowed."
            )

        return target
    
    ## list all files/folders in directory
    def list_directory(self, path: str = ".") -> dict:
        try:
            target = self._safe_path(path)

            if not target.exists():
                return {
                    "success": False,
                    "error": "Directory does not exist."
                }

            if not target.is_dir():
                return {
                    "success": False,
                    "error": "Path is not a directory."
                }

            # lists all files/directories
            entries = []

            for item in target.iterdir():
                entries.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file"
                })

            return {
                "success": True,
                "path": str(target.relative_to(self.project_root)),
                "entries": entries
            }

        except PermissionError as e:
            return {
                "success": False,
                "error": str(e)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Could not list directory: {e}"
            }
    ##  read file
    def read_file(self, path: str) -> dict:
        try:
            target = self._safe_path(path)
                        
            if not target.exists():
                return {
                    "success": False,
                    "error": "File does not exist."
                }

            if not target.is_file():
                return {
                    "success": False,
                    "error": "Path is not a file."
                }

            if target.stat().st_size > self.max_file_size:
                return {
                    "success": False,
                    "error": "File is too large."
                }

            content = target.read_text(
                encoding="utf-8"
            )

            return {
                "success": True,
                "path": str(target.relative_to(self.project_root)),
                "content": content
            }

        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "File is not a UTF-8 text file."
            }

        except PermissionError as e:
            return {
                "success": False,
                "error": str(e)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Could not read file: {e}"
            }