# 1Password Credential Lookup

Smart credential retrieval from 1Password using URL/domain and username filtering.

## When to Use

- Logging into websites via Playwright or browser automation
- Accessing services that require authentication
- When you know the URL but not the 1Password item name

## Key Principle: Search by URL, Filter by Username

**Never search by item title.** 1Password items often have arbitrary names that don't match usernames. Instead:

1. **Search by URL/domain** - Find all items associated with a website
2. **Filter by username** - When multiple accounts exist, filter by the known username

## MCP Tools

### `find_credential`
Primary tool for credential lookup. Searches by URL and optionally filters by username.

```
find_credential(url="twitter.com", username="clementwalter")
```

Returns:
- Single match: Full credentials (username, password, item_name, item_id)
- Multiple matches: List of available accounts to choose from
- No match: Error message

### `list_items_for_url`
Shows all 1Password items for a domain. Use when unsure which account to use.

```
list_items_for_url(url="github.com")
```

### `get_credential`
Direct lookup by item name or ID. Use only when you know the exact item.

## Domain Aliases

The tool handles common domain variations automatically:
- `x.com` ↔ `twitter.com` (same credentials)

## Workflow Example

```python
# Step 1: User wants to log into twitter.com as "clementwalter"
# Step 2: Use find_credential with URL + username
result = find_credential(url="twitter.com", username="clementwalter")

# If multiple accounts, tool returns list:
# {"message": "Multiple items found", "items": [...]}

# If single match or filtered match:
# {"username": "clementwalter", "password": "xxx", "item_name": "Twitter Personal"}
```

## Best Practices

1. **Always provide username when known** - Avoids ambiguity with multiple accounts
2. **Use domain, not full URL** - `github.com` not `https://github.com/login`
3. **Check list first if unsure** - `list_items_for_url` shows all options
4. **Handle multiple matches** - Prompt user to specify which account

## Error Handling

- "No items found" → Check domain spelling, try aliases
- "Multiple items found" → Add username filter
- "op CLI not installed" → User needs to install 1Password CLI
- "Timed out" → User needs to run `op signin`
