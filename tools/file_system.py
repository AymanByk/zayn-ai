from tools.project_context import ProjectContext
from typing import Optional
from pathlib import Path
import binascii
import tempfile
import shutil
import base64
import os
class FileSystemTool:

    def __init__(self, project_context: ProjectContext):

        self.project_context = project_context

        self.ignored_directories = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            "dist",
            "build"
        }

        self.max_file_size = 200 * 1024
    
    ## list all files/folders in directory
    def list_directory(self, path: str = ".") -> dict:
        try:
            target = self.project_context.resolve_path(path)

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
                "path": str(target.relative_to(self.project_context.get_project_root())),
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
    #  read file
    ## select specific lines of numbers, 
    ## or include line numbers 
    def read_file(self,
        path: str,
        include_line_numbers: bool = False,
        start_line: int | None = None,
        end_line: int | None = None
    ) -> dict:

        try:
            target = self.project_context.resolve_path(path)
                        
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

            file_size = target.stat().st_size

            if file_size > self.max_file_size:
                return {
                    "success": False,
                    "error": (
                        f"File is too large. "
                        f"Maximum allowed size is {self.max_file_size} bytes."
                    )
                }

            content = target.read_text(
                encoding="utf-8"
            )

            lines = content.splitlines()

            total_lines = len(lines)

            # validate line range
            if start_line is not None and start_line < 1:
                return {
                    "success": False,
                    "error": "start_line must be at least 1."
                }

            if end_line is not None and end_line < 1:
                return {
                    "success": False,
                    "error": "end_line must be at least 1."
                }

            if (start_line is not None
                and end_line is not None
                and start_line > end_line
            ):
                return {
                    "success": False,
                    "error": "start_line cannot be greater than end_line."
                }

            # convert to python indexes
            start_index = (
                start_line - 1
                if start_line is not None
                else 0
            )

            end_index = (
                end_line
                if end_line is not None
                else total_lines
            )

            selected_lines = lines[start_index:end_index]

            if include_line_numbers:
                selected_content = "\n".join(
                    f"{index}: {line}"
                    for index, line in enumerate(
                        selected_lines,
                        start=start_index + 1
                    )
                )
            else:
                selected_content = "\n".join(
                    selected_lines
                )

            relative_path = str(
                target.relative_to(
                    self.project_context.get_project_root()
                )
            )

            return {
                "success": True,
                "path": relative_path,
                "name": target.name,
                "extension": target.suffix,
                "size": file_size,
                "line_count": total_lines,
                "start_line": start_index + 1,
                "end_line": min(end_index,total_lines),
                "content": selected_content
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

        except OSError as e:
            return {
                "success": False,
                "error": f"Operating system error: {e}"
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

            if max_results < 1:
                return {
                    "success": False,
                    "error": "max_results must be at least 1."
                }

            # protection against unnecessary huge results
            max_results = min(max_results,100)
            results = []

            project_root = (
                self.project_context.get_project_root()
            )
            normalized_extension = None

            # Format the datatypes/extension
            if extension:
                normalized_extension = (
                    extension.lower().strip()
                )

                if not normalized_extension.startswith("."):
                    normalized_extension = (
                        "." + normalized_extension
                    )

            normalized_query = query.lower().strip()

            # Normalize content search term
            normalized_content = (
                content.lower()
                if content
                else None
            )

            # Recursively iterates through all files and directories
            # inside the active project
            for path in project_root.rglob("*"):
                #absolute to relative
                try:
                    relative_path = path.relative_to(
                        project_root
                    )

                except ValueError:
                    continue

                # ignore unwanted directories
                if any(
                    part in self.ignored_directories
                    for part in relative_path.parts
                ):
                    continue

                if not path.is_file():
                    continue

                # extension filter
                if normalized_extension:
                    if (path.suffix.lower() !=
                        normalized_extension):
                        continue

                # Filter files by filename 
                # if query provided
                if normalized_query:
                    if (normalized_query not in
                        path.name.lower()):
                        continue
                
                file_size = path.stat().st_size
                content_matches = []

                # optional content search
                if normalized_content:
                    if file_size > self.max_file_size:
                        continue

                    try:
                        text = path.read_text(encoding="utf-8")

                    # Skip binary, inaccessible or unreadable files
                    except (
                        UnicodeDecodeError,
                        PermissionError,
                        OSError
                    ):
                        continue

                    lines = text.splitlines()

                    # Search each line for the requested content
                    for line_number, line in enumerate(
                        lines,
                        start=1
                    ):
                        if (normalized_content
                            in line.lower()):
                            content_matches.append({
                                "line": line_number,
                                "preview": line.strip()[:200]
                            })

                            # avoid enormous match lists
                            if len(content_matches) >= 10:
                                break

                    if not content_matches:
                        continue

                results.append({
                    "path": str(relative_path),
                    "name": path.name,
                    "extension": path.suffix,
                    "size": file_size,
                    "matches": content_matches
                })

                if len(results) >= max_results:
                    break

            return {
                "success": True,
                "query": query,
                "extension": normalized_extension,
                "content": content,
                "results": results,
                "count": len(results),
                "max_results": max_results
            }

        except PermissionError as e:
            return {
                "success": False,
                "error": str(e)
            }

        except OSError as e:
            return {
                "success": False,
                "error": f"Operating system error: {e}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Could not search files: {e}"
            }

    def create_file(
        self,
        path: str,
        content: str = "",
        encoding: str = "utf-8"
    ) -> dict:
        try:
            # Validate path
            if not isinstance(path, str) or not path.strip() or Path(path).is_absolute():
                return {
                    "success": False,
                    "error": "Use a relative project path."
                    }

            # Validate content
            if not isinstance(content, str):
                return {
                    "success": False,
                    "error": "Content must be a string."
                    }
            # Validate encoding
            if encoding == "utf-8":
                data = content.encode("utf-8")
            elif encoding == "base64":
                data = base64.b64decode(content, validate=True)
            else:
                return {
                    "success": False,
                    "error": "Unsupported encoding."
                }

            # data limit
            if len(data) > 5 * 1024 * 1024:
                return {
                    "success": False,
                    "error": "File exceeds the 5 MB limit."
                }

            target = self.project_context.resolve_path(path)
            relative = target.relative_to(
                self.project_context.get_project_root()
            )

            if not relative.parts or any(
                part in self.ignored_directories for part in relative.parts
            ):
                return {
                    "success": False,
                    "error": "This project path is not writable."
                }

            # wrong directory
            if not target.parent.is_dir():
                return {
                    "success": False,
                    "error": "Parent directory does not exist."
                }

            # "x" creates new file or binary file.
            with target.open("xb") as file:
                file.write(data)

            return {
                "success": True,
                "path": str(relative),
                "size": len(data)
            }

        except (ValueError, binascii.Error):
            return {
                "success": False,
                "error": "Invalid Base64 content."
                }
        except FileExistsError:
            return {
                "success": False, 
                "error": "File already exists."
            }
        except PermissionError as error:
            return {
                "success": False,
                "error": str(error)
                }
        except OSError as error:
            return {
                "success": False,
                "error": f"Could not create file: {error}"
            }
    def replace_text(
        self,
        path: str,
        old_text: str,
        new_text: str,
        expected_content: str
    ) -> dict:
        try:
            # validating parameters
            if not isinstance(old_text, str) or not old_text:
                return {
                    "success": False,
                    "error": "old_text must be non-empty."
                }

            if not isinstance(new_text, str):
                return {
                    "success": False,
                    "error": "new_text must be a string."
                }

            target = self.project_context.resolve_path(path)

            # target ist not a file
            if not target.is_file():
                return {
                    "success": False,
                    "error": "File does not exist."
                }

            if target.stat().st_size > self.max_file_size:
                return {
                    "success": False,
                    "error": "File is too large."
                }

            # searches for matching lines
            with target.open("r", encoding="utf-8", newline="") as file:
                original = file.read()

            if original != expected_content:
                return {
                    "success": False,
                    "error": "File changed since approval. Read it again."
                }
            matches = original.count(old_text)
            
            # more than 1 occurence
            if matches != 1:
                return {
                    "success": False,
                    "error": f"Expected exactly one match, found {matches}."
                }

            # replace one occurence
            updated = original.replace(old_text, new_text, 1)

            if len(updated.encode("utf-8")) > self.max_file_size:
                return {
                    "success": False,
                    "error": "Updated file is too large."
                }
         
            # replace content
            self._write_text_atomic(
                target,
                updated,
                expected_content
            )

            return {
                "success": True,
                "path": str(target.relative_to(
                    self.project_context.get_project_root()
                ))
            }

        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "File is not UTF-8 text."
            }
        except PermissionError as error:
            return {
                "success": False,
                "error": str(error)
            }
        except OSError as error:
            return {
                "success": False,
                "error": str(error)
            }

    def delete_file(self, path: str, expected_state: tuple) -> dict:
        try:
            if not isinstance(path, str) or not path.strip() or Path(path).is_absolute():
                return {
                    "success": False,
                    "error": "Use a relative project path."
                }

            root = self.project_context.get_project_root()

            # symbolic links protection
            if (root / path).is_symlink():
                return {
                    "success": False,
                    "error": "Deleting symbolic links is not supported."
                }

            target = self.project_context.resolve_path(path)
            relative = target.relative_to(root)

            if any(
                part in self.ignored_directories
                for part in relative.parts
            ):
                return {
                    "success": False,
                    "error": "This project path is protected."
                }

            if not target.is_file():
                return {
                    "success": False,
                    "error": "Path is not an existing file."
                }

            # File same version before deletion?
            # Prüfen, ob noch dieselbe Dateiversion vorliegt.
            info = target.stat()
            current_state = (
                info.st_dev,
                info.st_ino,
                info.st_size,
                info.st_mtime_ns,
                info.st_ctime_ns
            )

            if current_state != expected_state:
                return {
                    "success": False,
                    "error": "File changed since approval. Try again."
                }

            target.unlink()

            return {
                "success": True,
                "path": str(relative)
            }

        except OSError as error:
            return {
                "success": False,
                "error": str(error)
            }
    
    def _write_text_atomic(
        self,
        target: Path,
        content: str,
        expected_content: str
    ) -> None:

        temp_path = None
        try:
            # create Temp file in same dir.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                dir=target.parent,
                prefix=".zayn_",
                suffix=".tmp",
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)
                temp_file.write(content)

            # check current result before replacing.
            with target.open("r", encoding="utf-8", newline="") as file:
                if file.read() != expected_content:
                    raise OSError(
                        "File changed since approval. Read it again."
                    )

            # authorization.
            shutil.copymode(target, temp_path)

            # replace the completed file.
            os.replace(temp_path, target)

        finally:
            # if error -> delet TempFile
            if temp_path is not None and temp_path.exists():
                temp_path.chmod(0o600)
                temp_path.unlink()