# --- Firestore（Native モード）---
resource "google_firestore_database" "default" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
  depends_on  = [google_project_service.enabled]
}

# --- Cloud Storage: 録音・成果物 ---
resource "google_storage_bucket" "recordings" {
  name                        = var.recordings_bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = false
  depends_on                  = [google_project_service.enabled]

  lifecycle_rule {
    condition { age = 90 } # 90日で自動削除（プライバシー配慮・要件に応じ調整）
    action { type = "Delete" }
  }
}

# --- Pub/Sub: 録音完了イベント ---
resource "google_pubsub_topic" "recording_done" {
  name       = "recording-done"
  depends_on = [google_project_service.enabled]
}

resource "google_pubsub_subscription" "recording_done_push" {
  name  = "recording-done-agent"
  topic = google_pubsub_topic.recording_done.id

  # agent-service の Cloud Run URL を後で設定（apply 後に push_config を更新）
  ack_deadline_seconds = 600
  expiration_policy { ttl = "" }
}

# --- Artifact Registry: コンテナイメージ ---
resource "google_artifact_registry_repository" "containers" {
  location      = var.region
  repository_id = "i2-lab-copilot"
  format        = "DOCKER"
  description   = "I2-Lab-Copilot container images"
  depends_on    = [google_project_service.enabled]
}
