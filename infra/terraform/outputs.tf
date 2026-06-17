output "service_account_email" {
  value = google_service_account.app.email
}

output "recordings_bucket" {
  value = google_storage_bucket.recordings.name
}

output "artifact_registry" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.containers.repository_id}"
}

output "pubsub_topic_recording_done" {
  value = google_pubsub_topic.recording_done.id
}

output "wif_provider" {
  description = "GitHub Actions の google-github-actions/auth に設定する値"
  value       = google_iam_workload_identity_pool_provider.github.name
}
