import os
import json
from deepdiff import DeepDiff
from datetime import datetime


def generate_changelog(v1_memo, v2_memo, account_id):
    diff = DeepDiff(v1_memo, v2_memo, ignore_order=True)
    
    changes = []

    # Fields that changed value
    for path, change in diff.get("values_changed", {}).items():
        changes.append({
            "field": str(path),
            "type": "updated",
            "old": str(change["old_value"]),
            "new": str(change["new_value"])
        })

    # New items added — FIX: convert to list first
    added = diff.get("dictionary_item_added", set())
    for path in list(added):
        changes.append({
            "field": str(path),
            "type": "added"
        })

    # Items removed — FIX: convert to list first
    removed = diff.get("dictionary_item_removed", set())
    for path in list(removed):
        changes.append({
            "field": str(path),
            "type": "removed"
        })

    # Items whose type changed
    for path, change in diff.get("type_changes", {}).items():
        changes.append({
            "field": str(path),
            "type": "type_changed",
            "old": str(change["old_value"]),
            "new": str(change["new_value"])
        })

    changelog = {
        "account_id": account_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_changes": len(changes),
        "changes": changes
    }

    # Save it
    out_dir = os.path.join(
        os.environ.get("OUTPUT_DIR", "./outputs/accounts"),
        account_id, "v2"
    )
    os.makedirs(out_dir, exist_ok=True)

    path = os.path.join(out_dir, "changes.json")
    with open(path, "w") as f:
        json.dump(changelog, f, indent=2)

    print(f"[CHANGELOG] {len(changes)} changes saved to: {path}")
    return changelog