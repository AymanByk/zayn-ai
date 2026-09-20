from pathlib import Path


class ProjectContext:

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.project_name = self.project_root.name

        if not self.project_root.exists():
            raise ValueError(
                f"Project root does not exist: {self.project_root}"
            )

        if not self.project_root.is_dir():
            raise ValueError(
                f"Project root is not a directory: {self.project_root}"
            )

    def get_project_root(self) -> Path:
        return self.project_root

    def get_project_name(self) -> str:
        return self.project_name

    # INFO
    def get_project_info(self) -> dict:
        return {
            "name": self.project_name,
            "root": str(self.project_root)
        }

    # Resolve-Path turns relative path into absolute
    def resolve_path(self, path: str) -> Path:
        target = (self.project_root / path).resolve()

        try:
            target.relative_to(self.project_root)

        except ValueError:
            raise PermissionError(
                "Access outside the project directory is not allowed."
            )

        return target