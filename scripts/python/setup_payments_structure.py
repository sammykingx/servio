import os

BASE_DIR = "app/payments"

# folder structure
folders = [
    "domain",
    "services",
    "infrastructure",
    "infrastructure/gateways",
    "infrastructure/gateways/stripe",
    "infrastructure/gateways/paystack",
    "infrastructure/gateways/flutterwave",
]

# files inside folders
files_with_comments = {
    # domain
    "domain/entities.py": "# Domain entities like Payment, EscrowTransaction, etc.\n",
    "domain/value_objects.py": "# Immutable value objects like Money, Currency, PaymentReference.\n",
    "domain/enums.py": "# Enums such as PaymentStatus, EscrowStatus, PaymentProvider.\n",
    "domain/contracts.py": "# Abstract contracts/interfaces for gateway adapters and services.\n",
    "domain/exceptions.py": "# Custom exceptions for payments domain.\n",
    "domain/policies.py": "# Business rules like EscrowReleasePolicy, RefundPolicy.\n",

    # services
    "services/payment_service.py": "# Core orchestration logic for processing payments.\n",
    "services/escrow_service.py": "# Handles escrow holding and releasing logic.\n",
    "services/refund_service.py": "# Handles refunds and provider refund requests.\n",

    # infrastructure gateways
    "infrastructure/gateways/stripe/adapter.py": "# Stripe gateway adapter implementing PaymentGateway contract.\n",
    "infrastructure/gateways/stripe/webhook_handler.py": "# Stripe webhook processing logic.\n",
    "infrastructure/gateways/paystack/adapter.py": "# Paystack gateway adapter implementing PaymentGateway contract.\n",
    "infrastructure/gateways/paystack/webhook_handler.py": "# Paystack webhook processing logic.\n",
    "infrastructure/gateways/flutterwave/adapter.py": "# Flutterwave gateway adapter implementing PaymentGateway contract.\n",
    "infrastructure/gateways/flutterwave/webhook_handler.py": "# Flutterwave webhook processing logic.\n",

    # infrastructure root
    "infrastructure/registry.py": "# Registry to resolve which payment gateway to use.\n",
    "infrastructure/repositories.py": "# Repositories to abstract database access for payments and transactions.\n",

}

# first-level files that require confirmation
root_files = {
    "tasks.py": "# Async tasks like verify_payment, retry_webhook, reconcile_transactions.\n",
}


def create_folder(path, comment=None):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created folder: {path}")
    else:
        print(f"Exists: {path}")

    # create __init__.py with folder comment
    init_file = os.path.join(path, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            if comment:
                f.write(f"# {comment}\n")
            else:
                f.write("# This package/module\n")
        print(f"Created __init__.py for {path}")


def create_file(path, comment):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(comment)
        print(f"Created file: {path}")
    else:
        print(f"Exists: {path}")


def confirm_create(path):
    while True:
        answer = input(f"{path} does not exist. Create it? (y/n): ").lower()
        if answer in ["y", "yes"]:
            return True
        elif answer in ["n", "no"]:
            return False


def main():
    print("\nSetting up payments module structure...\n")

    # Create base payments folder
    create_folder(BASE_DIR, "Payments app package for Django project")

    # Create subfolders with __init__.py
    folder_comments = {
        "domain": "Domain layer: entities, value objects, enums, contracts, exceptions, policies",
        "services": "Application layer: use-case services for payment, escrow, refund",
        "infrastructure": "Infrastructure layer: gateway adapters and repositories",
        "infrastructure/gateways": "Gateway integrations folder",
        "infrastructure/gateways/stripe": "Stripe gateway integration",
        "infrastructure/gateways/paystack": "Paystack gateway integration",
        "infrastructure/gateways/flutterwave": "Flutterwave gateway integration",
    }

    for folder in folders:
        path = os.path.join(BASE_DIR, folder)
        create_folder(path, folder_comments.get(folder))

    # Create nested files
    for file_path, comment in files_with_comments.items():
        full_path = os.path.join(BASE_DIR, file_path)
        create_file(full_path, comment)

    # Prompt and create first-level files
    for file_name, comment in root_files.items():
        full_path = os.path.join(BASE_DIR, file_name)
        if not os.path.exists(full_path):
            if confirm_create(full_path):
                create_file(full_path, comment)
            else:
                print(f"Skipped: {full_path}")
        else:
            print(f"Exists: {full_path}")

    print("\nPayments module scaffold complete.\n")


if __name__ == "__main__":
    main()
