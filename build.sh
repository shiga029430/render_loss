#!/usr/bin/env bash
# exit on error
set -o errexit

# 依存関係のインストール
pip install -r requirements.txt

# データベースのリセット
echo "Resetting database..."
python manage.py flush --no-input  # データベースをリセットして全てのデータを削除
python manage.py makemigrations  # マイグレーションファイルを作成
python manage.py migrate  # マイグレーションを適用

# 静的ファイルの収集
python manage.py collectstatic --no-input

# スーパーユーザーを自動で作成する
python manage.py superuser
