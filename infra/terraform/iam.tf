# アプリ用サービスアカウント（最小権限）
resource "google_service_account" "app" {
  account_id   = var.service_account_id
  display_name = "I2-Lab-Copilot application SA"
  depends_on   = [google_project_service.enabled]
}

locals {
  app_roles = [
    "roles/aiplatform.user",            # Vertex AI / Gemini
    "roles/speech.client",              # Speech-to-Text
    "roles/datastore.user",             # Firestore
    "roles/secretmanager.secretAccessor",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/cloudtasks.enqueuer",
    "roles/logging.logWriter",
    "roles/run.invoker",                # サービス間呼び出し
  ]
}

resource "google_project_iam_member" "app_roles" {
  for_each = toset(local.app_roles)
  project  = var.project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.app.email}"
}

# 録音バケットはオブジェクト権限のみ（プロジェクト全体には付与しない）
resource "google_storage_bucket_iam_member" "app_recordings" {
  bucket = google_storage_bucket.recordings.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.app.email}"
}
