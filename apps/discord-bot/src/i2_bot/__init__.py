"""i2_bot: Discord bot エントリポイント。

macOS の python.org ビルドは CA バンドルを持たず TLS 検証に失敗する。
discord(aiohttp) を import する前に certifi の CA を環境変数へ設定する必要があるため、
パッケージ読み込み時（submodule より前）にここで設定する。Linux(Cloud Run) では無害。
"""

import os

import certifi

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("SSL_CERT_DIR", os.path.dirname(certifi.where()))
