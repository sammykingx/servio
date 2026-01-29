BUSINESS_CATEGORIES_MAP = [
    {
      "name": "Home Services",
      "sub_categories": [
        "Handyman",
        "Plumber",
        "Electrician",
        "Carpenter",
        "Painter",
        "Gardener",
        "Cleaning",
        "Appliance Repair",
        "Pest Control",
        "Locksmith",
        "HVAC Technician",
        "Window Cleaning",
        "Flooring"
      ]
    },
    {
      "name": "Health & Wellness",
      "sub_categories": [
        "Personal Trainer",
        "Yoga Instructor",
        "Massage Therapist",
        "Nutritionist",
        "Hair Stylist",
        "Barber",
        "Makeup Artist",
        "Beauty Services",
        "Chiropractor",
        "Mental Health Counseling",
        "Dietician"
      ]
    },
    {
      "name": "Beauty & Personal Care",
      "sub_categories": [
        "Makeup Artist",
        "Hair Stylist",
        "Nail Technician",
        "Barber",
        "Esthetician",
        "Waxing Services",
        "Facial Treatments",
        "Hair Removal",
        "Bridal Makeup",
        "Tattoo Artist"
      ]
    },
    {
      "name": "Cleaning & Maintenance",
      "sub_categories": [
        "Home Cleaning",
        "Office Cleaning",
        "Carpet Cleaning",
        "Window Cleaning",
        "Deep Cleaning",
        "Post-Construction Cleaning",
        "Pressure Washing",
        "Pest Control",
        "Gutter Cleaning",
        "Tile & Grout Cleaning"
      ]
    },
    {
      "name": "Event Planning",
      "sub_categories": [
        "Wedding Planner",
        "Party Planner",
        "Event Decorator",
        "Catering Services",
        "Photographer",
        "Videographer",
        "DJ Services",
        "Florist",
        "Event Staffing",
        "Venue Finder",
        "Birthday Party Planning"
      ]
    },
    {
      "name": "Transportation",
      "sub_categories": [
        "Taxi Services",
        "Car Rental",
        "Ride Share Services",
        "Limo Services",
        "Airport Transfers",
        "Moving & Relocation",
        "Delivery Services",
        "Courier Services",
        "Bicycle Rentals"
      ]
    },
    {
      "name": "Technology & IT",
      "sub_categories": [
        "Web Development",
        "App Development",
        "Graphic Design",
        "UX/UI Design",
        "Software Development",
        "SEO & Digital Marketing",
        "Tech Support",
        "Network Setup",
        "Cloud Services",
        "IT Consulting",
        "Cybersecurity",
        "Data Recovery"
      ]
    },
    {
      "name": "Creative Services",
      "sub_categories": [
        "Photography",
        "Videography",
        "Graphic Design",
        "Logo Design",
        "Animation",
        "Voice-over Artist",
        "Content Writing",
        "Copywriting",
        "Video Editing",
        "Music Production",
        "Illustration",
        "Social Media Content"
      ]
    },
    {
      "name": "Legal Services",
      "sub_categories": [
        "Contract Drafting",
        "Legal Consultation",
        "Real Estate Lawyer",
        "Intellectual Property",
        "Divorce Lawyer",
        "Corporate Law",
        "Family Law",
        "Criminal Law",
        "Employment Law",
        "Notary Services",
        "Immigration Lawyer"
      ]
    },
    {
      "name": "Finance & Accounting",
      "sub_categories": [
        "Accounting Services",
        "Tax Preparation",
        "Financial Planning",
        "Bookkeeping",
        "Payroll Services",
        "Audit Services",
        "Business Consulting",
        "Investment Consulting",
        "Insurance Services"
      ]
    },
    {
      "name": "Education & Tutoring",
      "sub_categories": [
        "Private Tutoring",
        "Online Classes",
        "Test Preparation",
        "Language Learning",
        "Music Lessons",
        "Art Lessons",
        "STEM Tutoring",
        "Dance Lessons",
        "Homework Help"
      ]
    },
    {
      "name": "Real Estate",
      "sub_categories": [
        "Real Estate Agent",
        "Property Management",
        "Interior Design",
        "House Painting",
        "Landscaping",
        "Home Staging",
        "Real Estate Photography",
        "Real Estate Consulting",
        "Construction Services",
        "Moving Services"
      ]
    },
    {
      "name": "Marketing & Sales",
      "sub_categories": [
        "SEO Services",
        "PPC Campaign Management",
        "Social Media Marketing",
        "Content Marketing",
        "Email Marketing",
        "Affiliate Marketing",
        "Brand Strategy",
        "Market Research",
        "Sales Funnel Design",
        "Product Photography"
      ]
    },
    {
      "name": "Business Services",
      "sub_categories": [
        "Virtual Assistant",
        "Data Entry",
        "Customer Support",
        "Transcription Services",
        "Translation Services",
        "Business Consulting",
        "Project Management",
        "Market Research",
        "Recruitment Services"
      ]
    },
    {
      "name": "Construction & Renovation",
      "sub_categories": [
        "General Contractor",
        "Construction Project Manager",
        "Renovation Services",
        "Landscaping & Lawn Care",
        "Home Additions",
        "Remodeling",
        "Concrete Work",
        "Demolition Services",
        "Swimming Pool Installation",
        "Roofing Services"
      ]
    },
    {
      "name": "Food & Drink",
      "sub_categories": [
        "Catering",
        "Personal Chef",
        "Baking & Cake Design",
        "Bartending Services",
        "Private Dinner Parties",
        "Grocery Delivery",
        "Meal Prep Services"
      ]
    }
]

from typing import Dict, List, Union, Set

def get_industry_obj() -> List[Dict[str, str]]:
  return BUSINESS_CATEGORIES_MAP

def get_categories() -> Set:
  return {category.get("name") for category in BUSINESS_CATEGORIES_MAP}


def get_sub_categories(category:str) -> Union[List, None]:
  sub_category = None
  allowed_categories = get_categories()
  if category not in allowed_categories:
    return sub_category
  
  for category_obj in BUSINESS_CATEGORIES_MAP:
    if category_obj.get("name") == category:
      sub_category = category_obj.get("sub_categories")
  return sub_category

