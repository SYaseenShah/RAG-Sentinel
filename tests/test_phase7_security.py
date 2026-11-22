import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from security import auth, audit

class SecurityPhase7Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.users=Path(self.temp.name)/'users.json'
        self.logs=Path(self.temp.name)/'audit.jsonl'
        self.p1=patch.object(auth,'USERS_PATH',self.users); self.p1.start()
        self.p2=patch.object(audit,'AUDIT_PATH',self.logs); self.p2.start()
    def tearDown(self): self.p1.stop(); self.p2.stop(); self.temp.cleanup()
    def test_password_hash_and_login(self):
        auth.create_user('adminuser','StrongPassword123','admin')
        raw=self.users.read_text()
        self.assertNotIn('StrongPassword123',raw)
        self.assertEqual(auth.authenticate('adminuser','StrongPassword123')['role'],'admin')
        self.assertIsNone(auth.authenticate('adminuser','wrongpassword'))
    def test_password_policy(self):
        with self.assertRaises(ValueError): auth.create_user('abc','weak','admin')
    def test_duplicate_user_rejected(self):
        auth.create_user('abc','StrongPassword123','admin')
        with self.assertRaises(ValueError): auth.create_user('abc','StrongPassword123','viewer')
    def test_audit_event_and_secret_rejection(self):
        audit.log_event('admin','login_success',{'method':'password'})
        self.assertEqual(audit.read_events()[0]['event'],'login_success')
        with self.assertRaises(ValueError): audit.log_event('admin','login_success',{'password':'no'})
    def test_role_checks(self):
        self.assertTrue(auth.has_role({'role':'admin'},'admin'))
        self.assertFalse(auth.has_role({'role':'viewer'},'admin'))

if __name__=='__main__': unittest.main()
