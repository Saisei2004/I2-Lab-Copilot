locals {
  services = [
    "aiplatform.googleapis.com",        # Vertex AI / Gemini / ADK
    "speech.googleapis.com",            # Speech-to-Text v2
    "firestore.googleapis.com",         # Firestore
    "storage.googleapis.com",           # Cloud Storage
    "secretmanager.googleapis.com",     # Secret Manager
    "run.googleapis.com",               # Cloud Run
    "cloudbuild.googleapis.com",        # Cloud Build
    "artifactregistry.googleapis.com",  # Artifact Registry
    "pubsub.googleapis.com",            # Pub/Sub
    "cloudtasks.googleapis.com",        # Cloud Tasks
    "cloudscheduler.googleapis.com",    # Cloud Scheduler（将来の自動収集）
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",    # WIF
    "cloudresourcemanager.googleapis.com",
  ]
}

resource "google_project_service" "enabled" {
  for_each = toset(local.services)
  service  = each.value

  disable_on_destroy = false
}
