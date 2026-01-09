---
description: Deduplicate 1Password entries with same username (keeps one per username)
allowed-tools: []
---

# Deduplicate 1Password Entries

Run the 1Password deduplication script. This will find entries with duplicate usernames and keep only one of each.

**IMPORTANT:** This command handles sensitive credential data. Do NOT request or display any output from the script. Simply confirm to the user that the deduplication process has been initiated.

Execute the dedup script:

```bash
${CLAUDE_PLUGIN_ROOT}/commands/dedup.py
```

After execution, tell the user: "Deduplication complete. Check your terminal for any prompts from 1Password."
