
import os
import django
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from collaboration.models.gigs import Gig
from collaboration.models.gigrole import GigRole
from collaboration.models.gig_category import GigCategory
from collaboration.models.choices import GigStatus, GigVisibility, RoleStatus
from collaboration.oppurtunities.views.list import OppurtunityListView
from django.test import RequestFactory
from django.db.models import Exists, OuterRef, Prefetch, Q

User = get_user_model()

def run():
    print("Setting up test data...")
    
    # Clean up
    Gig.objects.all().delete()
    User.objects.all().delete()
    GigCategory.objects.all().delete()

    # Create Categories
    tech_parent = GigCategory.objects.create(name="Tech", slug="tech", parent=None)
    backend_niche = GigCategory.objects.create(name="Backend", slug="backend", parent=tech_parent)
    design_parent = GigCategory.objects.create(name="Design", slug="design", parent=None)
    ui_niche = GigCategory.objects.create(name="UI/UX", slug="ui-ux", parent=design_parent)

    # Create User with Backend niche
    user = User.objects.create_user(email="dev@example.com", password="password")
    # Using defaults for profile creation signals if any, otherwise create manually
    if not hasattr(user, 'profile'):
        from accounts.models import UserProfile
        UserProfile.objects.create(user=user)
    
    user.profile.industry = tech_parent
    user.profile.niches.add(backend_niche)
    user.profile.save()

    # Create Match Gig (Backend role)
    match_gig = Gig.objects.create(
        title="Backend Gig",
        creator=User.objects.create_user(email="client1@example.com", password="password"),
        status=GigStatus.PENDING,
        visibility=GigVisibility.PUBLIC,
        total_budget=Decimal("1000.00"),
        has_gig_roles=True,
        description="A backend gig"
    )
    GigRole.objects.create(
        gig=match_gig,
        niche=backend_niche,
        budget=Decimal("500.00"),
        status=RoleStatus.OPEN
    )

    # Create Non-Match Gig (UI/UX role)
    non_match_gig = Gig.objects.create(
        title="Design Gig",
        creator=User.objects.create_user(email="client2@example.com", password="password"),
        status=GigStatus.PENDING,
        visibility=GigVisibility.PUBLIC,
        total_budget=Decimal("1000.00"),
        has_gig_roles=True,
        description="A design gig"
    )
    GigRole.objects.create(
        gig=non_match_gig,
        niche=ui_niche,
        budget=Decimal("500.00"),
        status=RoleStatus.OPEN
    )

    # Create General Gig (No roles)
    general_gig = Gig.objects.create(
        title="General Gig",
        creator=User.objects.create_user(email="client3@example.com", password="password"),
        status=GigStatus.PENDING,
        visibility=GigVisibility.PUBLIC,
        total_budget=Decimal("1000.00"),
        has_gig_roles=False,
        description="A general gig"
    )
    
    # Mixed Gig (Has both Backend (match) and UI (non-match) - Should appear and show Backend role)
    mixed_gig = Gig.objects.create(
        title="Mixed Gig",
        creator=User.objects.create_user(email="client4@example.com", password="password"),
        status=GigStatus.PENDING,
        visibility=GigVisibility.PUBLIC,
        total_budget=Decimal("2000.00"),
        has_gig_roles=True,
        description="A mixed gig"
    )
    GigRole.objects.create(
        gig=mixed_gig,
        niche=backend_niche,
        budget=Decimal("500.00"),
        status=RoleStatus.OPEN
    )
    GigRole.objects.create(
        gig=mixed_gig,
        niche=ui_niche,
        budget=Decimal("500.00"),
        status=RoleStatus.OPEN
    )

    print("Data setup complete.")

    # Simulate View Logic
    view = OppurtunityListView()
    request = RequestFactory().get('/gigs/')
    request.user = user
    view.request = request
    
    qs = view.get_queryset()
    
    print(f"\nQueryset count: {qs.count()}")
    
    print("\nResults (Title - Matched Roles):")
    for gig in qs:
        matched_role_names = []
        if hasattr(gig, 'matched_roles'):
             matched_role_names = [r.niche.name for r in gig.matched_roles]
        
        # Check ordering key if we added it (we haven't yet in the code, but script will run after we do)
        is_relevant = getattr(gig, 'is_relevant', 'N/A')
        
        print(f"- {gig.title} (Relevant: {is_relevant}) roles: {matched_role_names}")


run()
