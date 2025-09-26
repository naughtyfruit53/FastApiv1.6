#!/bin/bash

# SnappyMail auto-config entrypoint

# Set variables from env
ADMIN_USER="${SNAPPYMAIL_ADMIN_USER:-admin}"
ADMIN_PASS="${SNAPPYMAIL_ADMIN_PASS}"

CONFIG_DIR="/var/www/html/data/_data_/_default_/configs"
APPLICATION_INI="${CONFIG_DIR}/application.ini"

# Ensure data directory exists and has correct permissions
mkdir -p "${CONFIG_DIR}"
chown -R www-data:www-data /var/www/html/data
chmod -R 755 /var/www/html/data

# If admin pass set in env, generate hash and update application.ini
if [ -n "${ADMIN_PASS}" ]; then
  # Create application.ini if not exists (basic template)
  if [ ! -f "${APPLICATION_INI}" ]; then
    echo "[security]" > "${APPLICATION_INI}"
    echo "admin_login = '${ADMIN_USER}'" >> "${APPLICATION_INI}"
    echo "[logs]" >> "${APPLICATION_INI}"
    echo "[labs]" >> "${APPLICATION_INI}"
    echo "[cache]" >> "${APPLICATION_INI}"
    echo "[plugins]" >> "${APPLICATION_INI}"
    # Add more sections if needed, but minimal for start
  fi

  # Generate PHP password hash
  HASH=$(php -r "echo password_hash('${ADMIN_PASS}', PASSWORD_DEFAULT);")

  # Update or add admin_login and admin_password in [security]
  if grep -q "^admin_login" "${APPLICATION_INI}"; then
    sed -i "s/^admin_login = .*/admin_login = '${ADMIN_USER}'/" "${APPLICATION_INI}"
  else
    sed -i "/\[security\]/a admin_login = '${ADMIN_USER}'" "${APPLICATION_INI}"
  fi

  if grep -q "^admin_password" "${APPLICATION_INI}"; then
    sed -i "s/^admin_password = .*/admin_password = '${HASH}'/" "${APPLICATION_INI}"
  else
    sed -i "/\[security\]/a admin_password = '${HASH}'" "${APPLICATION_INI}"
  fi

  echo "Admin user/pass configured in application.ini"
fi

# Start Apache
exec apache2-foreground