#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> 1. Installing Python dependencies..."
pip install -r requirements.txt

echo "==> 2. Collecting static files..."
python manage.py collectstatic --no-input

echo "==> 3. Running database migrations..."
python manage.py migrate

echo "==> 4. Seeding official BookLeaf sample dataset (1 Admin, 10 Authors, 18 Books)..."
python manage.py seed_sample_data

echo "==> [✓] Build and Seeding Complete!"
