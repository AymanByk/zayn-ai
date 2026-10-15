
class ToolPolicy:

    # Tools that can run without user approval
    AUTO = {
        "time",
        "calculator",
        "get_memory",
        "list_memories",
        "list_directory",
        "read_file",
        "search_files",
        "get_project_info",
        "remember",
        "forget",
        "swap_value"
    }

    # Tools that require user approval
    APPROVAL = {
        "create_file",
        "replace_text",
        "delete_file",
        "write_file"
    }

    def get_permission(self, tool_name: str) -> str:

        if tool_name in self.AUTO:
            return "auto"

        if tool_name in self.APPROVAL:
            return "approval"

        # Unknown tools are blocked by default
        return "deny"
