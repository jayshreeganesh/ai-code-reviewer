import re
from typing import List, Dict, Any, Optional
from unidiff import PatchSet

class FileChange:
    def __init__(self, file_path: str, is_new: bool = False, is_deleted: bool = False):
        self.file_path = file_path
        self.is_new = is_new
        self.is_deleted = is_deleted
        self.added_lines: List[Dict[str, Any]] = []    # [{"line_no": 12, "content": "..."}]
        self.deleted_lines: List[Dict[str, Any]] = []  # [{"line_no": 10, "content": "..."}]
        self.hunks: List[Dict[str, Any]] = []
        self.raw_patch: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "is_new": self.is_new,
            "is_deleted": self.is_deleted,
            "added_lines": self.added_lines,
            "deleted_lines": self.deleted_lines,
            "raw_patch": self.raw_patch
        }

class DiffParser:
    """
    Parses unified diffs, Git patches, or raw code blocks into structured
    file changes and mapped line numbers for inline review annotations.
    """

    def parse(self, diff_text: str) -> List[FileChange]:
        clean_text = diff_text.strip()
        if not clean_text:
            return []

        # Attempt 1: Standard unidiff parser
        try:
            patch_set = PatchSet(clean_text)
            if patch_set and len(patch_set) > 0:
                results = []
                for patched_file in patch_set:
                    file_path = patched_file.path
                    if file_path.startswith("b/") or file_path.startswith("a/"):
                        file_path = file_path[2:]

                    fc = FileChange(
                        file_path=file_path,
                        is_new=patched_file.is_added_file,
                        is_deleted=patched_file.is_removed_file
                    )
                    fc.raw_patch = str(patched_file)

                    for hunk in patched_file:
                        hunk_dict = {
                            "source_start": hunk.source_start,
                            "target_start": hunk.target_start,
                            "lines": []
                        }
                        for line in hunk:
                            if line.is_added:
                                fc.added_lines.append({
                                    "line_no": line.target_line_no,
                                    "content": line.value.rstrip("\r\n")
                                })
                            elif line.is_removed:
                                fc.deleted_lines.append({
                                    "line_no": line.source_line_no,
                                    "content": line.value.rstrip("\r\n")
                                })
                            hunk_dict["lines"].append({
                                "type": "+" if line.is_added else ("-" if line.is_removed else " "),
                                "line_no": line.target_line_no if line.is_added else line.source_line_no,
                                "content": line.value.rstrip("\r\n")
                            })
                        fc.hunks.append(hunk_dict)
                    results.append(fc)

                if results:
                    return results
        except Exception:
            pass

        # Attempt 2: Regex-based unified diff fallback
        return self._regex_fallback_parse(clean_text)

    def _regex_fallback_parse(self, text: str) -> List[FileChange]:
        """
        Regex fallback for non-standard diff headers or raw code snippets.
        """
        results: List[FileChange] = []
        file_splits = re.split(r"(?:^|\n)diff --git ", text)

        for part in file_splits:
            part = part.strip()
            if not part:
                continue

            # Determine file name
            file_match = re.search(r"^\s*a/(.*?)\s+b/(.*?)(?:\n|$)", part)
            if file_match:
                file_path = file_match.group(2)
            else:
                fn_match = re.search(r"(?:---|\+\+\+)\s+[ab]/(.*?)(?:\n|$)", part)
                file_path = fn_match.group(1) if fn_match else "source_code.py"

            fc = FileChange(file_path=file_path)
            fc.raw_patch = part

            # Parse @@ hunks
            hunk_matches = list(re.finditer(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@([^\n]*)", part))
            if hunk_matches:
                for i, hm in enumerate(hunk_matches):
                    target_start = int(hm.group(2))
                    start_pos = hm.end()
                    end_pos = hunk_matches[i + 1].start() if i + 1 < len(hunk_matches) else len(part)
                    hunk_body = part[start_pos:end_pos]

                    curr_line = target_start
                    for raw_line in hunk_body.splitlines():
                        if not raw_line:
                            continue
                        prefix = raw_line[0]
                        line_content = raw_line[1:]
                        if prefix == "+":
                            fc.added_lines.append({"line_no": curr_line, "content": line_content})
                            curr_line += 1
                        elif prefix == "-":
                            fc.deleted_lines.append({"line_no": None, "content": line_content})
                        else:
                            curr_line += 1
            else:
                # Raw code snippet without diff markers
                lines = part.splitlines()
                for idx, line in enumerate(lines, start=1):
                    fc.added_lines.append({"line_no": idx, "content": line})

            results.append(fc)

        return results

diff_parser_service = DiffParser()
