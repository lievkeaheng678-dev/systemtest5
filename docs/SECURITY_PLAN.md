# Security Plan / ផែនការការពារសុវត្ថិភាព

## English

| Area | Measure |
|---|---|
| Passwords | Hashed with PBKDF2; minimum 8 characters; common/numeric/similar passwords rejected |
| Brute force | Username locked 15 minutes after 5 failed logins |
| Authorization | Groups (Administrator, Staff Manager, Member) with least-privilege permissions |
| View protection | `@login_required` for all private pages; `@permission_required` for user list, toggle, audit log |
| Sessions | DB-backed, 30-minute idle timeout, expire on browser close, HttpOnly + SameSite cookies |
| CSRF / Clickjacking | CSRF tokens on every form, logout is POST-only, `X_FRAME_OPTIONS = DENY` |
| Audit | Login, logout, failed login, register, profile edit, activate/deactivate recorded with IP and browser; read-only in admin |
| Production | HTTPS redirect, secure cookies, HSTS, secret key from environment, `DEBUG=0` |
| Backups | Back up PostgreSQL regularly (`pg_dump identity_db > backup.sql`) |

## ខ្មែរ

| ផ្នែក | វិធានការ |
|---|---|
| ពាក្យសម្ងាត់ | រក្សាទុកជាទម្រង់ Hash (PBKDF2) យ៉ាងតិច ៨ តួអក្សរ ហាមប្រើពាក្យសម្ងាត់ងាយៗ |
| ការវាយប្រហារដោយសាកល្បងច្រើនដង | ចាក់សោឈ្មោះអ្នកប្រើ ១៥ នាទី បន្ទាប់ពីចូលខុស ៥ ដង |
| ការកំណត់សិទ្ធិ | ក្រុមការងារ (Administrator, Staff Manager, Member) ផ្តល់សិទ្ធិតិចបំផុតតាមតម្រូវការ |
| ការការពារទំព័រ | `@login_required` សម្រាប់ទំព័រឯកជន និង `@permission_required` សម្រាប់ទំព័រគ្រប់គ្រង |
| សម័យប្រើប្រាស់ (Sessions) | ផុតកំណត់ក្រោយ ៣០ នាទីដែលមិនប្រើ ឬពេលបិទ Browser |
| CSRF / Clickjacking | មាន CSRF token ក្នុងគ្រប់ Form, Logout ប្រើ POST, `X_FRAME_OPTIONS = DENY` |
| កំណត់ត្រាសវនកម្ម | កត់ត្រាការចូល ចេញ ចូលខុស ចុះឈ្មោះ កែប្រែព័ត៌មាន ជាមួយ IP |
| ផលិតកម្ម | បង្ខំ HTTPS, Cookie សុវត្ថិភាព, HSTS, `DEBUG=0` |
| ការបម្រុងទុក | បម្រុងទុក PostgreSQL ជាប្រចាំ (`pg_dump`) |
