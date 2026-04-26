---
name: Bug Report
about: Create a report to help us improve
title: "[BUG] "
labels: bug
assignees: ''
---

## Description

<!-- A clear description of the bug -->

## Steps to Reproduce

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior

<!-- What did you expect to happen? -->

## Actual Behavior

<!-- What actually happened? Include error messages, logs, screenshots -->

## Environment

- **OS**: [e.g., Ubuntu 22.04, macOS 14, Windows 11]
- **Python version**: [e.g., 3.12.0]
- **Installation method**: [uv/pip, Docker, etc.]
- **Medicare Rebate Checker version**: [e.g., 1.0.0]

## Additional Context

<!-- Any other context about the problem: logs, configuration, etc. -->

### Configuration (sanitized)

```env
# Paste relevant .env values (remove secrets)
APP_ENV=development
LOG_LEVEL=INFO
```

### MBS Item & Patient Data (if applicable)

```json
{
  "mbs_item": "13200",
  "age": 35,
  "has_medicare_card": true
}
```

### Error Output

```
Paste full traceback or log output here
```