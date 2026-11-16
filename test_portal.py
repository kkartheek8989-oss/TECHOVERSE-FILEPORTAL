from app import app
from database import init_db, get_db

init_db()
client = app.test_client()

print("[*] Running Verification Suite for TechnoVault Portal...")

# 1. Test Home page
res1 = client.get('/')
print(f"  [+] Home Page Status: {res1.status_code}")
assert res1.status_code == 200

# 2. Test Circulars page (Public notice board)
res2 = client.get('/circulars')
print(f"  [+] Circulars Page Status: {res2.status_code}")
assert res2.status_code == 200

# 3. Test Login page
res3 = client.get('/login')
print(f"  [+] Login Page Status: {res3.status_code}")
assert res3.status_code == 200

# 4. Test Public File Direct Download (Anonymous allowed)
conn = get_db()
cursor = conn.cursor()
cursor.execute("SELECT id, filename FROM files WHERE classification = 'public' LIMIT 1")
pub_file = cursor.fetchone()
print(f"  [+] Testing Public Download for File #{pub_file['id']} ({pub_file['filename']})...")
res4 = client.get(f"/file/{pub_file['id']}/download")
print(f"      Status: {res4.status_code}, Received {len(res4.data)} bytes")
assert res4.status_code == 200

# 5. Test Confidential File Protection (Unauthenticated anonymous download blocked)
cursor.execute("SELECT id, filename FROM files WHERE classification = 'confidential' LIMIT 1")
conf_file = cursor.fetchone()
print(f"  [+] Testing Confidential Security on File #{conf_file['id']} ({conf_file['filename']})...")
res5 = client.get(f"/file/{conf_file['id']}/download", follow_redirects=False)
print(f"      Unauthenticated download redirected with status: {res5.status_code}")
assert res5.status_code == 302, "Should redirect unauthorized user"

# 6. Test Login as Core Committee Member and Authorized Confidential Download
with client.session_transaction() as sess:
    sess['user_id'] = 2
    sess['username'] = 'core_lead'
    sess['role'] = 'core'
    sess['full_name'] = 'Kartheek (President)'

# Confidential file has secondary PIN '7788'
res6 = client.get(f"/file/{conf_file['id']}/download?pin=7788")
print(f"      Authenticated Core Lead + PIN download status: {res6.status_code}, Received {len(res6.data)} bytes")
assert res6.status_code == 200

conn.close()
print("\n[SUCCESS] ALL SECURITY & WORKFLOW VERIFICATIONS PASSED 100%!")
