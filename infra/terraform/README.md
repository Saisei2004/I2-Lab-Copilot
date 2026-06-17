# infra/terraform

GCP リソースを IaC 管理する。作成物:

- API 有効化（Vertex AI / Speech / Firestore / Run / Pub/Sub ほか）
- アプリ用サービスアカウント `i2-copilot-sa` と最小権限ロール
- Firestore (Native) / GCS バケット（録音, 90日ライフサイクル）
- Pub/Sub トピック `recording-done`
- Artifact Registry（Docker）
- Workload Identity Federation（GitHub Actions → GCP, 鍵レス）

## 使い方
```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## 注意
- `terraform.tfvars` と `*.tfstate` は gitignore 済み。
- Secret Manager のシークレット値は Terraform では管理しない（runbook の手順で投入）。
- Pub/Sub の push 先（agent-service URL）は Cloud Run デプロイ後に設定する。
