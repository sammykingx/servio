from enum import Enum
from uuid import UUID


class DurationUnit(str, Enum):
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    
    
MOCK_PROPOSAL_PAYLOAD = {
  "project_id":  UUID("019b9e827ae274eea0c1154570086b57"), #"550e8400-e29b-41d4-a716-446655440000",
  "value": 2500.00,
  "currency": "USD",
  "sent_at": "2026-05-15T15:30:00Z",
  "applied_roles": [
    {
      "industry_id": 1,
      "niche_id": 12,
      "niche_name": "Fullstack Engineering",
      "role_amount": 2500.00,
      "payment_plan": "50_50",
      "deliverables": [
        {
          "order": 1,
          "title": "System Architecture",
          "description": "Designing the database schema and cloud infrastructure.",
          "duration_unit": "weeks",
          "duration_value": 2,
          "release_percentage": 30.0
        },
        {
          "order": 2,
          "title": "API Implementation",
          "description": "Building the core CRUD endpoints and auth logic.",
          "duration_unit": "months",
          "duration_value": 1,
          "release_percentage": 70.0
        }
      ]
    }
  ]
}

MALFORMED_PROPOSAL_PAYLOAD = {
  "project_id": "not-a-uuid", 
  "value": 2.00, 
  "currency": "GBP", 
  "sent_at": "invalid-date",
  "applied_roles": [
    {
      "industry_id": 1,
      "niche_id": 12,
      "niche_name": "Frontend Designer",
      "role_amount": 1000.00,
      "deliverables": [
        {
          "order": 1,
          "title": "UI Mockups",
          "description": "      leading and trailing spaces should be stripped      ",
          "duration_unit": "days",
          "duration_value": 25, 
          "release_percentage": 110.0 
        }
      ]
    }
  ]
}