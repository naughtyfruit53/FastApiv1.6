#!/bin/sh

set -e

DATA_DIR=/var/www/html/data

# Check if application.ini exists; if not, create it with env vars for MySQL and admin
if [ ! -f "$DATA_DIR/_default_/configs/application.ini" ]; then
  echo "Initializing SnappyMail configuration..."

  mkdir -p "$DATA_DIR/_default_/configs"

  cat << EOF > "$DATA_DIR/_default_/configs/application.ini
[general]
language = en
theme = default
allow_themes = On
allow_languages_on_settings = On

[security]
admin_login = $SNAPPYMAIL_ADMIN_USER

[database]
type = mysql
host = $SNAPPYMAIL_DB_HOST
port = 3306
name = $SNAPPYMAIL_DB_NAME
user = $SNAPPYMAIL_DB_USER
password = $SNAPPYMAIL_DB_PASS
EOF

  # Hash the admin password using PHP (SnappyMail uses password_hash)
  php -r "file_put_contents('$DATA_DIR/_default_/admin_password.txt', password_hash('$SNAPPYMAIL_ADMIN_PASS', PASSWORD_DEFAULT));"

  # Set permissions
  chown -R www-data:www-data "$DATA_DIR"
  echo "SnappyMail initialized with MySQL config and admin password."
fi

# Start Apache
exec apache2-foreground