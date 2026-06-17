variable "project_id" {
  type        = string
  description = "GCP プロジェクト ID"
  default     = "nakazawa-laborary"
}

variable "region" {
  type        = string
  description = "デフォルトリージョン"
  default     = "asia-northeast1"
}

variable "service_account_id" {
  type        = string
  description = "アプリ用サービスアカウント ID"
  default     = "i2-copilot-sa"
}

variable "recordings_bucket_name" {
  type        = string
  description = "録音保存用 GCS バケット名（グローバル一意）"
  default     = "i2-lab-copilot-recordings"
}

variable "github_repo" {
  type        = string
  description = "WIF を許可する GitHub リポジトリ (owner/repo)"
  default     = "Saisei2004/I2-Lab-Copilot"
}
