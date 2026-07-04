def assemble_draft_stub(draft_version: int) -> dict:
    return {
        "draft_version": draft_version + 1,
        "approval_status": "draft",
        "status": "running",
    }
