-- PostgreSQL pgcrypto trigger for automatic encryption of user personal data
-- This trigger encrypts email, phone, and address fields before storing in the database

-- Create pgcrypto extension if it doesn't exist
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Drop existing trigger and function if they exist (for re-creation)
DROP TRIGGER IF EXISTS users_encrypt_trigger ON users;
DROP FUNCTION IF EXISTS encrypt_user_fields() CASCADE;

-- Create trigger function to encrypt user personal information
-- The function reads the encryption key from PostgreSQL application settings
-- Set via: SELECT set_config('app.pgcrypto_key', key_value, false);
CREATE OR REPLACE FUNCTION encrypt_user_fields()
RETURNS TRIGGER AS $$
DECLARE
  encryption_key TEXT;
BEGIN
  -- Get encryption key from current_setting
  -- This will be set by the Python application at startup
  encryption_key := current_setting('app.pgcrypto_key', true);
  
  -- Only proceed if key is set
  IF encryption_key IS NULL OR encryption_key = '' THEN
    RAISE WARNING 'pgcrypto encryption key not set (app.pgcrypto_key)';
    RETURN NEW;
  END IF;
  
  -- Encrypt email if provided
  -- Input is bytes (UTF-8 encoded plaintext), convert to text for pgp_sym_encrypt
  IF NEW.email_encrypted IS NOT NULL THEN
    NEW.email_encrypted := pgp_sym_encrypt(
      convert_from(NEW.email_encrypted, 'UTF8'),
      encryption_key
    );
  END IF;
  
  -- Encrypt phone if provided
  IF NEW.phone_encrypted IS NOT NULL THEN
    NEW.phone_encrypted := pgp_sym_encrypt(
      convert_from(NEW.phone_encrypted, 'UTF8'),
      encryption_key
    );
  END IF;
  
  -- Encrypt address if provided
  IF NEW.address_encrypted IS NOT NULL THEN
    NEW.address_encrypted := pgp_sym_encrypt(
      convert_from(NEW.address_encrypted, 'UTF8'),
      encryption_key
    );
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger that fires before INSERT or UPDATE
CREATE TRIGGER users_encrypt_trigger
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION encrypt_user_fields();

-- Grant execute permission to public (if needed for other roles)
-- GRANT EXECUTE ON FUNCTION encrypt_user_fields() TO public;
