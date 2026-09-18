from pathlib import Path


class FileSystemTool:

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()

        self.ignored_directories = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            "dist",
            "build"
        }

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
    ## searchFile
    # Searches for files/dictionaries with specific parameters
    # Query hint  to filename, extension for type of data file, 
    # content searches for text within a fil,  max_result  limits amount of results
    def search_files(
        self,
        query: str = "",
        extension: str | None = None,
        content: str | None = None,
        max_results: int = 50
    ) -> dict:

        try:
            results = []
            # iters through all directories in the current project
            for path in self.project_root.rglob("*"):

                relative_parts = path.relative_to(
                    self.project_root
                ).parts

                if any(part in self.ignored_directories
                    for part in relative_parts):
                    continue



                if not path.is_file():
                    continue

                # extension filter
                if extension:
                    normalized_extension = extension.lower()

                    if not normalized_extension.startswith("."):
                        normalized_extension = "." + normalized_extension

                    if path.suffix.lower() != normalized_extension:
                        continue

                # filename search
                if query:
                    if query.lower() not in path.name.lower():
                        continue

                # optional content search
                if content:
                    try:
                        if path.stat().st_size > self.max_file_size:
                            continue

                        text = path.read_text(
                            encoding="utf-8"
                        )

                        if content.lower() not in text.lower():
                            continue

                    except (
                        UnicodeDecodeError,
                        PermissionError,
                        OSError
                    ):
                        continue

                results.append({
                    "path": str(
                        path.relative_to(self.project_root)
                    ),
                    "name": path.name,
                    "extension": path.suffix,
                    "size": path.stat().st_size
                })

                if len(results) >= max_results:
                    break

            return {
                "success": True,
                "query": query, 
                "extension": extension,
                "content": content,
                "results": results,
                "count": len(results)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Could not search files: {e}"
            }