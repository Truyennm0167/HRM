# PostgreSQL Setup Guide

## 📋 Prerequisites

- Windows 10/11
- Administrator access
- Stable internet connection

---

## 🐘 PostgreSQL Installation

### Method 1: Official Installer (Recommended)

#### Step 1: Download PostgreSQL

1. Visit: https://www.postgresql.org/download/windows/
2. Click "Download the installer"
3. Choose version: **PostgreSQL 18.x** (latest stable)
4. Download 64-bit version

#### Step 2: Install PostgreSQL

1. Run the installer as Administrator
2. Installation directory: `C:\Program Files\PostgreSQL\18`
3. Select components:

   - ✅ PostgreSQL Server
   - ✅ pgAdmin 4
   - ✅ Stack Builder (optional)
   - ✅ Command Line Tools

4. Data directory: `C:\Program Files\PostgreSQL\18\data`

5. **Set password for postgres user**:

   - Choose a strong password
   - **Remember this password!**
   - Example: `admin` (for development)

6. Port: `5432` (default)

7. Locale: `Default locale`

8. Complete installation (may take 5-10 minutes)

#### Step 3: Verify Installation

Open PowerShell as Administrator:

```powershell
# Add PostgreSQL to PATH (if not already)
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"

# Check version
psql --version
# Expected: psql (PostgreSQL) 18.x

# Test connection
psql -U postgres
# Enter password when prompted
# You should see: postgres=#
```

### Method 2: Using Docker (Alternative)

```powershell
# Pull PostgreSQL image
docker pull postgres:18

# Run PostgreSQL container
docker run --name hrm-postgres `
  -e POSTGRES_PASSWORD=postgres123 `
  -e POSTGRES_DB=hrm_db `
  -p 5432:5432 `
  -d postgres:18

# Verify container is running
docker ps
```

---

## 🗄️ Database Setup

### Option A: Using pgAdmin 4 (GUI)

1. **Open pgAdmin 4** (installed with PostgreSQL)

2. **Connect to PostgreSQL Server**:

   - Right-click "Servers" → "Register" → "Server"
   - Name: `HRM Local`
   - Host: `localhost`
   - Port: `5432`
   - Username: `postgres`
   - Password: (your postgres password)

3. **Create Database**:

   - Right-click "Databases" → "Create" → "Database"
   - Database name: `hrm_db`
   - Owner: `postgres`
   - Encoding: `UTF8`
   - Click "Save"

4. **Create User (Optional - for security)**:

   - Right-click "Login/Group Roles" → "Create" → "Login/Group Role"
   - Name: `hrm_user`
   - Password: `hrm_password123`
   - Privileges: ✅ Can login
   - Click "Save"

5. **Grant Permissions**:
   - Right-click `hrm_db` → "Properties"
   - Go to "Security" tab
   - Add `hrm_user` with ALL PRIVILEGES

### Option B: Using Command Line (psql)

```powershell
# Connect to PostgreSQL
psql -U postgres

# Inside psql console:
CREATE DATABASE hrm_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

# Create dedicated user (recommended)
CREATE USER hrm_user WITH PASSWORD 'hrm_password123';

# Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE hrm_db TO hrm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hrm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hrm_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO hrm_user;

# Exit psql
\q
```

---

## 🔧 Django Configuration

### Step 1: Install Required Packages

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install psycopg2 (PostgreSQL adapter)
pip install psycopg2-binary

# Update requirements.txt
pip freeze > requirements.txt
```

### Step 2: Update Environment Variables

Create or update `.env` file:

```env
# Database Configuration
USE_SQLITE=0
USE_POSTGRESQL=1

# PostgreSQL Settings
POSTGRES_DB=hrm_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Or use dedicated user
# POSTGRES_USER=hrm_user
# POSTGRES_PASSWORD=hrm_password123

# Other settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 3: Verify Configuration

```powershell
# Test database connection
python manage.py shell
```

In Python shell:

```python
from django.db import connection
print(connection.settings_dict)
# Should show PostgreSQL configuration

# Test connection
with connection.cursor() as cursor:
    cursor.execute("SELECT version();")
    print(cursor.fetchone())
# Should show PostgreSQL version
```

---

## 🔄 Data Migration Process

### Complete Migration Steps

```powershell
# 1. Backup SQLite data
python backup_sqlite_data.py
# Creates: backups/sqlite_backup_YYYYMMDD_HHMMSS/

# 2. Update .env to use PostgreSQL
# Set USE_SQLITE=0 and USE_POSTGRESQL=1

# 3. Create PostgreSQL schema
python manage.py migrate
# This creates all tables in PostgreSQL

# 4. Restore data from backup
python restore_postgresql_data.py backups/sqlite_backup_YYYYMMDD_HHMMSS

# 5. Verify data
python manage.py shell
```

In shell:

```python
from django.contrib.auth.models import User
from app.models import Employee, Department

print(f"Users: {User.objects.count()}")
print(f"Employees: {Employee.objects.count()}")
print(f"Departments: {Department.objects.count()}")
```

---

## ✅ Post-Migration Checklist

### 1. Verify Database Connection

```powershell
python manage.py dbshell
```

In psql:

```sql
-- Check tables
\dt

-- Check record counts
SELECT COUNT(*) FROM auth_user;
SELECT COUNT(*) FROM app_employee;
SELECT COUNT(*) FROM app_department;

-- Exit
\q
```

### 2. Test Admin Panel

```powershell
python manage.py runserver
```

Visit: http://localhost:8000/admin/

- Login with existing superuser
- Check if all data is visible

### 3. Run Tests

```powershell
python manage.py test app
python manage.py test ai_recruitment
```

### 4. Check Sequences (Important!)

PostgreSQL uses sequences for auto-increment fields. After data import:

```sql
-- In psql
SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user));
SELECT setval('app_employee_id_seq', (SELECT MAX(id) FROM app_employee));
SELECT setval('app_department_id_seq', (SELECT MAX(id) FROM app_department));
-- Repeat for all tables with auto-increment IDs
```

Or use Django management command:

```powershell
python manage.py sqlsequencereset app | python manage.py dbshell
```

---

## 🐛 Troubleshooting

### Issue 1: "psql is not recognized"

**Solution**: Add PostgreSQL to PATH

```powershell
# Temporary (current session)
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"

# Permanent (all sessions)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\PostgreSQL\18\bin", "Machine")
```

### Issue 2: "peer authentication failed"

**Solution**: Edit `pg_hba.conf`

Location: `C:\Program Files\PostgreSQL\18\data\pg_hba.conf`

Change:

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     peer
```

To:

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
```

Restart PostgreSQL:

```powershell
Restart-Service postgresql-x64-18
```

### Issue 3: "role does not exist"

**Solution**: Create the user

```sql
CREATE USER hrm_user WITH PASSWORD 'hrm_password123';
GRANT ALL PRIVILEGES ON DATABASE hrm_db TO hrm_user;
```

### Issue 4: Port 5432 already in use

**Solution**: Check what's using the port

```powershell
# Find process using port 5432
netstat -ano | findstr :5432

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change PostgreSQL port in postgresql.conf
```

### Issue 5: Cannot create tables

**Error**: "permission denied for schema public"

**Solution**:

```sql
GRANT ALL ON SCHEMA public TO hrm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hrm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hrm_user;
```

### Issue 6: Encoding errors

**Solution**: Ensure database uses UTF8

```sql
-- Drop and recreate with correct encoding
DROP DATABASE hrm_db;
CREATE DATABASE hrm_db
    WITH
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';
```

---

## 📊 Performance Optimization

### Create Indexes (After Migration)

```sql
-- Indexes for frequent queries
CREATE INDEX idx_employee_user ON app_employee(user_id);
CREATE INDEX idx_employee_department ON app_employee(department_id);
CREATE INDEX idx_leaverequest_employee ON app_leaverequest(employee_id);
CREATE INDEX idx_contract_employee ON app_contract(employee_id);

-- Full-text search indexes
CREATE INDEX idx_employee_name ON app_employee USING gin(to_tsvector('english', first_name || ' ' || last_name));
```

### Configure PostgreSQL

Edit `postgresql.conf`:

```conf
# Memory Settings (adjust based on your system)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 16MB

# Checkpoint Settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB

# Query Planning
random_page_cost = 1.1  # SSD optimization
```

Restart PostgreSQL after changes.

---

## 🔒 Security Best Practices

1. **Use Strong Passwords**:

   ```powershell
   # Generate secure password
   Add-Type -AssemblyName System.Web
   [System.Web.Security.Membership]::GeneratePassword(16, 4)
   ```

2. **Restrict Remote Access**:

   - Edit `pg_hba.conf`
   - Only allow specific IPs

3. **Regular Backups**:

   ```powershell
   # Create backup
   pg_dump -U postgres -d hrm_db -F c -f backups/hrm_db_$(Get-Date -Format 'yyyyMMdd').backup

   # Restore from backup
   pg_restore -U postgres -d hrm_db -c backups/hrm_db_20241116.backup
   ```

4. **Enable SSL** (Production):
   - Generate SSL certificates
   - Configure in `postgresql.conf`

---

## 📚 Useful Commands

### PostgreSQL Service Management

```powershell
# Start PostgreSQL
Start-Service postgresql-x64-18

# Stop PostgreSQL
Stop-Service postgresql-x64-18

# Restart PostgreSQL
Restart-Service postgresql-x64-18

# Check status
Get-Service postgresql-x64-18
```

### Database Management

```sql
-- List databases
\l

-- Connect to database
\c hrm_db

-- List tables
\dt

-- Describe table
\d app_employee

-- Show table size
SELECT pg_size_pretty(pg_total_relation_size('app_employee'));

-- Show database size
SELECT pg_size_pretty(pg_database_size('hrm_db'));

-- Kill connections to database
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'hrm_db' AND pid <> pg_backend_pid();
```

### Backup & Restore

```powershell
# Backup database
pg_dump -U postgres -d hrm_db -F c -f hrm_backup.dump

# Restore database
pg_restore -U postgres -d hrm_db -c hrm_backup.dump

# Backup as SQL
pg_dump -U postgres -d hrm_db > hrm_backup.sql

# Restore from SQL
psql -U postgres -d hrm_db < hrm_backup.sql
```

---

## 🎯 Quick Start Summary

```powershell
# 1. Install PostgreSQL
# Download from postgresql.org and install

# 2. Create database
psql -U postgres -c "CREATE DATABASE hrm_db;"

# 3. Install Python package
pip install psycopg2-binary

# 4. Backup SQLite
python backup_sqlite_data.py

# 5. Update .env
# Set USE_SQLITE=0, USE_POSTGRESQL=1

# 6. Migrate schema
python manage.py migrate

# 7. Restore data
python restore_postgresql_data.py backups/sqlite_backup_YYYYMMDD_HHMMSS

# 8. Test
python manage.py runserver
```

---

**Last Updated**: November 16, 2024  
**PostgreSQL Version**: 18.x  
**Django Version**: 4.2.16
