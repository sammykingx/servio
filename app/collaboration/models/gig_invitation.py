"""
Docstring for servio-app.collaboration.models.gig_invitation

GigInvitation
- id
- gig_id (FK → Gig)
- professional_id (FK → User)
- invited_by_id (FK → User)
- status (pending | accepted | declined | expired)
- message (optional)
- created_at
- expires_at (optional)

"""