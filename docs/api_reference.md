# API Reference

## FastAPI REST Endpoints

Base URL: `http://localhost:8000` (default)

### GET /

Returns basic API information.

**Response**:
```json
{
  "name": "Medicare Rebate Eligibility Checker API",
  "version": "1.0.0",
  "status": "operational",
  "docs": "/docs",
  "health": "/health"
}
```

### GET /health

Health check endpoint for liveness probes.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-26T14:31:29.123456",
  "version": "1.0.0"
}
```

### POST /check-rebate

Check rebate eligibility and calculate amounts.

**Request Body** (application/json):
```json
{
  "mbs_item": "13200",
  "age": 35,
  "has_medicare_card": true,
  "concession_status": false,
  "hospital_status": false,
  "has_referral": false,
  "output_format": "markdown"
}
```

**Response**:
```json
{
  "eligible": true,
  "rebate_amount": 39.75,
  "gap_fee": 0.0,
  "schedule_fee": 39.75,
  "mbs_item": "13200",
  "description": "GP Consultation (Level B)",
  "reason": "Eligible",
  "processing_time_ms": 89.12,
  "report_path": "reports/rebate_13200_20260426_143022.md"
}
```

**Error Responses**:
- `400` – Validation error (missing fields, invalid types)
- `404` – MBS item not found
- `500` – Internal server error

### GET /mbs-items/{item_number}

Retrieve details for a specific MBS item.

**Response**: JSON object containing item details.

### GET /mbs-items

List all MBS items, with optional filtering.

**Query Parameters**:
- `category` (optional): Filter by category name
- `search` (optional): Search in description text

**Response**:
```json
{
  "count": 20,
  "items": [
    {
      "item_number": "13200",
      "description": "GP Consultation (Level B)",
      "category": "General Practice",
      "schedule_fee": 39.75
    },
    ...
  ]
}
```

### GET /reports/{filename}

Download a generated report file.

**Parameters**:
- `filename`: Name of the report file (e.g., `rebate_13200_20260426_143022.md`)

**Response**: File content with appropriate MIME type.

---

## CLI Reference

### Usage

```bash
python src/app/cli.py --mbs-item ITEM --age AGE [options]
```

### Arguments

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--mbs-item` | str | Yes | MBS item number (e.g., 13200) |
| `--age` | int | Yes | Patient age in years |
| `--has-medicare-card` | boolean | Yes | Whether patient has Medicare card |
| `--concession-status` | boolean | No | Patient concession status (default: False) |
| `--hospital-status` | boolean | No | Hospital admission status (default: False) |
| `--has-referral` | boolean | No | Referral status (default: False) |
| `--output-format` | str | No | Report format: markdown, json, html (default: markdown) |
| `--output-dir` | str | No | Directory for reports (default: reports/) |

### Example

```bash
python src/app/cli.py --mbs-item 13200 --age 35 --has-medicare-card True
```

Output:
```
🔍 MBS Item: 13200
✅ Eligible for rebate: $39.75
💰 Gap fee: $0.00
📄 Report saved to: reports/rebate_13200_20260426.md
```