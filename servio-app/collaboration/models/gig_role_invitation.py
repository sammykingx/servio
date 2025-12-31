"""
Docstring for servio-app.collaboration.models.gig_role_invitation

GigRoleInvitation
- id
- gig_role_id (FK → GigRole)
- professional_id (FK → User)
- invited_by_id (FK → User)
- status (pending | accepted | declined | expired)
- created_at

"""