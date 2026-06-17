terraform {
  required_version = ">= 1.7"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
  # 本番では GCS backend を推奨（state 共有）。初期はローカル state。
  # backend "gcs" {
  #   bucket = "nakazawa-laborary-tfstate"
  #   prefix = "i2-lab-copilot"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
