#!/bin/sh

set -e

DATA_DIR=/var/www/html/data
CONFIG_DIR="$DATA_DIR/_data_/_default_/configs"
APPLICATION_INI="$CONFIG_DIR/application.ini"
ADMIN_USER="${SNAPPYMAIL_ADMIN_USER:-admin}"
ADMIN_PASS="${SNAPPYMAIL_ADMIN_PASS}"

# Ensure data and config directories exist with correct permissions
mkdir -p "$CONFIG_DIR"
chown -R www-data:www-data "$DATA_DIR"
chmod -R 755 "$DATA_DIR"

# Create or update application.ini with basic config, including MySQL PDO and admin security
echo "Initializing or updating SnappyMail configuration..."

if [ ! -f "$APPLICATION_INI" ]; then
  cat << EOF > "$APPLICATION_INI"
[general]
language = en
theme = default
allow_themes = On
allow_languages_on_settings = On

[security]
admin_login = '$ADMIN_USER'

[pdo]
type = 'mysql'
host = '$SNAPPYMAIL_DB_HOST'
port = 3306
name = '$SNAPPYMAIL_DB_NAME'
user = '$SNAPPYMAIL_DB_USER'
password = '$SNAPPYMAIL_DB_PASS'
EOF
fi

# Always disable TOTP 2FA for admin
if grep -q "^admin_totp" "$APPLICATION_INI"; then
  sed -i "s/^admin_totp = .*/admin_totp = ''/" "$APPLICATION_INI"
else
  sed -i "/\[security\]/a admin_totp = ''" "$APPLICATION_INI"
fi

# If admin pass set, generate hash and add/update in [security]
if [ -n "$ADMIN_PASS" ]; then
  HASH=$(php -r "echo password_hash('$ADMIN_PASS', PASSWORD_DEFAULT);")
  if grep -q "^admin_password" "$APPLICATION_INI"; then
    sed -i "s/^admin_password = .*/admin_password = '$HASH'/" "$APPLICATION_INI"
  else
    sed -i "/\[security\]/a admin_password = '$HASH'" "$APPLICATION_INI"
  fi
  echo "Admin password hashed and set in application.ini"
fi

# Remove any initial admin_password.txt to avoid conflicts
rm -f "$DATA_DIR/_data_/_default_/admin_password.txt"

echo "SnappyMail initialized with MySQL PDO config, admin settings, and TOTP disabled."

# Start Apache
exec apache2-foreground