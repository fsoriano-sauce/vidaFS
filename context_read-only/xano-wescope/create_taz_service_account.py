#!/usr/bin/env python3
"""
Create a service account 'taz' with comprehensive but safe permissions for a personal assistant.

This creates a 'personal assistant' service account that can perform most GCP operations
but cannot modify IAM policies, user accounts, or perform other dangerous operations.
"""

import os
import sys
import json
from typing import List, Dict, Set, Optional
from google.cloud import iam_admin
from google.api_core.exceptions import AlreadyExists, PermissionDenied
from google.oauth2 import service_account
import google.auth


def get_current_project_info() -> Dict[str, str]:
    """Get current project and user information."""
    print("🔍 Getting current project and user information...")

    # Get current credentials
    credentials, project_id = google.auth.default()

    if not credentials:
        print("❌ No GCP credentials found. Please authenticate with: gcloud auth login")
        sys.exit(1)

    # Try to get the current user's email from credentials
    user_email = None
    is_service_account = False

    if hasattr(credentials, 'service_account_email'):
        user_email = credentials.service_account_email
        is_service_account = True
    elif hasattr(credentials, 'signer_email'):
        user_email = credentials.signer_email
        is_service_account = True

    if not user_email:
        print("❌ Could not determine current user email from credentials")
        print("   Please ensure you're authenticated with gcloud auth login")
        sys.exit(1)

    print(f"👤 Current user: {user_email}")
    print(f"📁 Current project: {project_id}")

    # Check if this is a service account (not a user account)
    if is_service_account and "@" in user_email and user_email.endswith(".iam.gserviceaccount.com"):
        print("\n⚠️  WARNING: You appear to be authenticated as a service account, not a user account.")
        print("   Service accounts typically don't have permission to create other service accounts.")
        print("   This script needs to be run with your personal GCP user credentials.")
        print("\n🔑 To authenticate with your personal account:")
        print("   1. Run: gcloud auth login")
        print("   2. Follow the browser authentication flow")
        print("   3. Re-run this script")
        print("\n❌ Cannot proceed with service account authentication.")
        sys.exit(1)

    return {
        "user_email": user_email,
        "project_id": project_id
    }


def get_safe_permissions() -> List[str]:
    """Get a comprehensive set of safe permissions for a personal assistant."""
    print("🛡️  Defining safe permissions for personal assistant...")

    # Comprehensive but safe permissions - excluding IAM management and user modification
    safe_permissions = [
        # BigQuery permissions
        "bigquery.datasets.create",
        "bigquery.datasets.get",
        "bigquery.datasets.getIamPolicy",
        "bigquery.datasets.update",
        "bigquery.jobs.create",
        "bigquery.jobs.get",
        "bigquery.jobs.list",
        "bigquery.jobs.listAll",
        "bigquery.models.create",
        "bigquery.models.delete",
        "bigquery.models.getData",
        "bigquery.models.getMetadata",
        "bigquery.models.list",
        "bigquery.models.updateData",
        "bigquery.models.updateMetadata",
        "bigquery.routines.create",
        "bigquery.routines.delete",
        "bigquery.routines.get",
        "bigquery.routines.list",
        "bigquery.routines.update",
        "bigquery.tables.create",
        "bigquery.tables.delete",
        "bigquery.tables.get",
        "bigquery.tables.getData",
        "bigquery.tables.list",
        "bigquery.tables.update",
        "bigquery.tables.updateData",

        # Cloud Storage permissions
        "storage.buckets.create",
        "storage.buckets.get",
        "storage.buckets.list",
        "storage.buckets.update",
        "storage.objects.create",
        "storage.objects.delete",
        "storage.objects.get",
        "storage.objects.list",
        "storage.objects.update",

        # Cloud Functions
        "cloudfunctions.functions.call",
        "cloudfunctions.functions.create",
        "cloudfunctions.functions.delete",
        "cloudfunctions.functions.get",
        "cloudfunctions.functions.list",
        "cloudfunctions.functions.update",

        # Cloud Run
        "run.services.create",
        "run.services.delete",
        "run.services.get",
        "run.services.list",
        "run.services.update",

        # Cloud Build
        "cloudbuild.builds.create",
        "cloudbuild.builds.get",
        "cloudbuild.builds.list",

        # Secret Manager (read-only)
        "secretmanager.versions.access",

        # Logging
        "logging.logEntries.create",
        "logging.logEntries.list",
        "logging.logs.list",

        # Monitoring
        "monitoring.metricDescriptors.get",
        "monitoring.metricDescriptors.list",
        "monitoring.timeSeries.list",

        # Pub/Sub
        "pubsub.subscriptions.consume",
        "pubsub.subscriptions.create",
        "pubsub.subscriptions.delete",
        "pubsub.subscriptions.get",
        "pubsub.subscriptions.list",
        "pubsub.subscriptions.update",
        "pubsub.topics.create",
        "pubsub.topics.delete",
        "pubsub.topics.get",
        "pubsub.topics.list",
        "pubsub.topics.publish",
        "pubsub.topics.update",

        # Compute Engine (basic)
        "compute.instances.create",
        "compute.instances.delete",
        "compute.instances.get",
        "compute.instances.list",
        "compute.instances.reset",
        "compute.instances.start",
        "compute.instances.stop",
        "compute.instances.update",

        # Service Management (read-only)
        "servicemanagement.services.get",
        "servicemanagement.services.list",

        # Service Usage
        "serviceusage.services.get",
        "serviceusage.services.list",
        "serviceusage.services.enable",
        "serviceusage.services.disable",
    ]

    print(f"✅ Defined {len(safe_permissions)} safe permissions")
    return safe_permissions


def create_custom_role(project_id: str, role_id: str, permissions: List[str], title: str, description: str) -> str:
    """Create a custom role with the specified permissions."""
    iam_client = iam_admin.IAMClient()

    role_name = f"projects/{project_id}/roles/{role_id}"

    role = iam_admin.Role()
    role.title = title
    role.description = description
    role.included_permissions = permissions
    role.stage = iam_admin.Role.RoleLaunchStage.BETA

    try:
        request = iam_admin.CreateRoleRequest(
            parent=f"projects/{project_id}",
            role_id=role_id,
            role=role
        )
        created_role = iam_client.create_role(request=request)
        print(f"✅ Created custom role: {created_role.name}")
        return created_role.name
    except AlreadyExists:
        print(f"ℹ️  Role {role_name} already exists")
        return role_name
    except Exception as e:
        print(f"❌ Failed to create role {role_name}: {e}")
        return None


def create_service_account(project_id: str, account_id: str, display_name: str, description: str) -> Optional[str]:
    """Create a service account."""
    iam_client = iam_admin.IAMClient()

    service_account = iam_admin.ServiceAccount()
    service_account.display_name = display_name
    service_account.description = description

    try:
        request = iam_admin.CreateServiceAccountRequest(
            name=f"projects/{project_id}",
            account_id=account_id,
            service_account=service_account
        )
        created_account = iam_client.create_service_account(request=request)
        service_account_email = created_account.email
        print(f"✅ Created service account: {service_account_email}")
        return service_account_email
    except AlreadyExists:
        service_account_email = f"{account_id}@{project_id}.iam.gserviceaccount.com"
        print(f"ℹ️  Service account {service_account_email} already exists")
        return service_account_email
    except Exception as e:
        print(f"❌ Failed to create service account {account_id}: {e}")
        return None


def create_service_account_key(project_id: str, service_account_email: str, output_file: str):
    """Create and download a service account key."""
    iam_client = iam_admin.IAMClient()

    service_account_name = f"projects/{project_id}/serviceAccounts/{service_account_email}"

    try:
        # Create key
        key = iam_client.create_service_account_key(
            name=service_account_name,
            private_key_type=iam_admin.ServiceAccountPrivateKeyType.TYPE_GOOGLE_CREDENTIALS_FILE
        )

        # Save to file
        with open(output_file, 'wb') as f:
            f.write(key.private_key_data)

        print(f"✅ Service account key saved to: {output_file}")
        print("🔐 Keep this key secure! It provides full access to your GCP resources.")

        # Also save as JSON for easier use
        key_data = json.loads(key.private_key_data.decode('utf-8'))
        json_file = output_file.replace('.json', '_credentials.json')
        with open(json_file, 'w') as f:
            json.dump(key_data, f, indent=2)

        print(f"✅ JSON credentials also saved to: {json_file}")

    except Exception as e:
        print(f"❌ Failed to create service account key: {e}")


def main():
    """Main function to create the 'taz' service account."""
    print("🤖 GCP Service Account Creator - 'taz'")
    print("=" * 50)

    # Get current project and user info
    project_info = get_current_project_info()
    user_email = project_info["user_email"]
    project_id = project_info["project_id"]

    print(f"\n📋 Configuration:")
    print(f"   User: {user_email}")
    print(f"   Project: {project_id}")

    # Create service account
    print("\n👤 Creating service account 'taz-assistant'...")
    service_account_email = create_service_account(
        project_id=project_id,
        account_id="taz-assistant",
        display_name="Taz - Personal Assistant",
        description=f"Personal assistant service account for {user_email} with comprehensive permissions"
    )

    if not service_account_email:
        print("❌ Failed to create service account. Cannot proceed.")
        sys.exit(1)

    # Grant standard roles to the service account using gcloud
    print("\n🔑 Granting roles to service account...")

    standard_roles = [
        "roles/bigquery.admin",      # Full BigQuery access
        "roles/storage.admin",       # Full Cloud Storage access
        "roles/viewer",              # Basic read access across GCP
        "roles/logging.admin",       # Logging access
        "roles/monitoring.viewer",   # Monitoring read access
        "roles/pubsub.admin",        # Pub/Sub access
        "roles/cloudfunctions.admin", # Cloud Functions access
        "roles/run.admin",           # Cloud Run access
        "roles/cloudbuild.builds.editor", # Cloud Build access
        "roles/secretmanager.secretAccessor", # Secret Manager read access
    ]

    import subprocess
    for role in standard_roles:
        print(f"   Granting {role}...")
        try:
            cmd = [
                "gcloud", "projects", "add-iam-policy-binding", project_id,
                "--member", f"serviceAccount:{service_account_email}",
                "--role", role,
                "--quiet"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"   ✅ Granted {role}")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Failed to grant {role}: {e.stderr}")
        except FileNotFoundError:
            print("   ❌ gcloud command not found. Please install Google Cloud SDK.")
            sys.exit(1)

    # Create service account key
    print("\n🔐 Creating service account key...")
    key_file = f"taz_service_account_key_{project_id}.json"
    create_service_account_key(project_id, service_account_email, key_file)

    print("\n🎉 SUCCESS! Service account 'taz' has been created!")
    print("=" * 50)
    print(f"Service Account: {service_account_email}")
    print(f"Key File: {key_file}")
    print("\n✅ Capabilities:")
    print("   - Same permissions as you (minus account modification)")
    print("   - Can manage GCP resources, BigQuery, Cloud Storage, etc.")
    print("   - Cannot modify or delete your personal GCP account")
    print("   - Cannot modify IAM policies or user accounts")
    print("\n⚠️  SECURITY REMINDERS:")
    print("   - Keep the key file secure and never commit it to version control")
    print("   - Use this service account for automated tasks and scripts")
    print("   - Regularly rotate service account keys")
    print("   - Monitor service account usage in GCP IAM audit logs")
    print("\n🚀 To use this service account:")
    print(f"   export GOOGLE_APPLICATION_CREDENTIALS='{key_file}'")
    print("   # Then run your GCP commands/scripts as usual")
if __name__ == "__main__":
    main()
