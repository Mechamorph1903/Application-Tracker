# SQLite to Supabase PostgreSQL Migration Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Database Differences](#database-differences)
4. [Migration Process](#migration-process)
5. [Configuration Setup](#configuration-setup)
6. [Running the Migration](#running-the-migration)
7. [Post-Migration Tasks](#post-migration-tasks)
8. [Testing and Verification](#testing-and-verification)
9. [Troubleshooting](#troubleshooting)
10. [Key Concepts Explained](#key-concepts-explained)

## Overview

This document explains the migration process from SQLite (local database) to Supabase PostgreSQL (cloud database) for the Flask Internship Tracker application. The migration involves transferring data structure (schema) and all existing data while maintaining application functionality.

### Why Migrate?

**SQLite Limitations:**
- Single-user database (no concurrent access)
- Limited data types
- No built-in user authentication
- File-based storage (not cloud-ready)
- No real-time subscriptions

**Supabase PostgreSQL Benefits:**
- Multi-user support with concurrent access
- Rich data types (JSON, arrays, custom types)
- Built-in authentication and authorization
- Cloud-hosted with automatic backups
- Real-time subscriptions
- REST API auto-generation
- Row Level Security (RLS)

## Prerequisites

Before starting the migration, ensure you have:

1. **Supabase Account**: Sign up at https://supabase.com
2. **New Supabase Project**: Created with a secure password
3. **Python Environment**: Virtual environment with required packages
4. **Database Access**: Connection details from Supabase dashboard
5. **Backup**: Current SQLite database backup

## Database Differences

### SQLite vs PostgreSQL Data Types

| SQLite | PostgreSQL | Notes |
|--------|------------|-------|
| INTEGER | SERIAL/INTEGER | PostgreSQL has auto-incrementing SERIAL |
| TEXT | VARCHAR/TEXT | PostgreSQL supports length limits |
| REAL | DECIMAL/FLOAT | PostgreSQL has precise decimal types |
| BLOB | BYTEA | PostgreSQL binary data type |
| JSON (extension) | JSON/JSONB | PostgreSQL has native JSON support |

### Key Differences

1. **Auto-incrementing IDs**:
   - SQLite: `INTEGER PRIMARY KEY AUTOINCREMENT`
   - PostgreSQL: `SERIAL PRIMARY KEY` or `BIGSERIAL PRIMARY KEY`

2. **Boolean Values**:
   - SQLite: Stores as 0/1 integers
   - PostgreSQL: Native BOOLEAN type with true/false

3. **JSON Storage**:
   - SQLite: TEXT field with JSON content
   - PostgreSQL: Native JSON or JSONB with indexing and querying

4. **Date/Time**:
   - SQLite: TEXT or INTEGER
   - PostgreSQL: TIMESTAMP, DATE, TIME types with timezone support

## Migration Process

### Phase 1: Schema Creation

The migration script creates tables in PostgreSQL that match your Flask models:

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    major VARCHAR(100),
    graduation_year INTEGER,
    location VARCHAR(200),
    bio TEXT,
    profile_picture VARCHAR(255),
    social_media JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    password_changed_at TIMESTAMP
);

-- Internships table
CREATE TABLE internships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    company VARCHAR(200) NOT NULL,
    position VARCHAR(200) NOT NULL,
    location VARCHAR(200),
    status VARCHAR(50) DEFAULT 'applied',
    date_applied DATE,
    application_deadline DATE,
    description TEXT,
    salary_range VARCHAR(100),
    notes TEXT,
    contacts JSON,
    next_action VARCHAR(200),
    next_action_date DATE,
    next_action_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Friendships table
CREATE TABLE friendships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    friend_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, friend_id)
);
```

### Phase 2: Data Migration

The script transfers data row by row, handling:
- Data type conversions
- JSON field formatting
- Date/time formatting
- Null value handling
- Foreign key relationships

### Phase 3: Verification

After migration, the script verifies:
- Record counts match
- Sample data integrity
- Foreign key relationships
- JSON data structure

## Configuration Setup

### Step 1: Get Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **Database**
3. Find the **Connection String** section
4. Copy the PostgreSQL connection string

### Step 2: Create Environment File

1. Copy `.env.template` to `.env`:
   ```cmd
   copy .env.template .env
   ```

2. Edit `.env` with your actual credentials:
   ```env
   SUPABASE_DB_URL=postgresql://postgres:your_password@db.yourprojectref.supabase.co:5432/postgres
   ```

3. Replace `your_password` with your database password
4. Replace `yourprojectref` with your project reference

### Step 3: Install Dependencies

Ensure you have the required Python packages:
```cmd
pip install psycopg2-binary python-dotenv
```

## Running the Migration

### Step 1: Verify Environment

```cmd
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✓ Environment loaded' if os.getenv('SUPABASE_DB_URL') else '✗ SUPABASE_DB_URL not found')"
```

### Step 2: Run Migration Script

```cmd
python migrate_to_supabase.py
```

### Step 3: Monitor Progress

The script provides detailed output:
- 🏗️ Schema creation progress
- 📊 Data migration progress with counts
- ✅ Verification results
- ⚠️ Any warnings or errors

## Post-Migration Tasks

### Step 1: Update Flask Configuration

1. Install PostgreSQL adapter:
   ```cmd
   pip install psycopg2-binary
   ```

2. Update `app/__init__.py` to use PostgreSQL:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   # Replace SQLite URI with PostgreSQL
   app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SUPABASE_DB_URL')
   ```

3. Update `requirements.txt`:
   ```txt
   psycopg2-binary==2.9.7
   python-dotenv==1.0.0
   ```

### Step 2: Test Database Connection

Create a test script to verify connectivity:
```python
from app import create_app, db
from app.models import User, Internship

app = create_app()
with app.app_context():
    # Test database connection
    users = User.query.all()
    internships = Internship.query.all()
    print(f"Found {len(users)} users and {len(internships)} internships")
```

### Step 3: Handle File Uploads

If using profile pictures:
1. Consider migrating to Supabase Storage
2. Or keep files local and update paths
3. Update file storage logic in `app/utils/file_storage.py`

## Testing and Verification

### Functional Tests

1. **Authentication**: Login/logout, registration
2. **Applications**: Create, read, update, delete internships
3. **Profile**: Update user information, social media
4. **Friends**: Send/accept friend requests
5. **Search**: Application filtering and search
6. **Export**: CSV/Excel export functionality

### Data Integrity Tests

1. **User Data**: Verify all user profiles migrated
2. **Internship Data**: Check all applications and their details
3. **Relationships**: Confirm friendships are intact
4. **JSON Fields**: Verify contacts and social media data
5. **Dates**: Ensure proper date formatting

### Performance Tests

1. **Query Speed**: Compare response times
2. **Concurrent Users**: Test multiple simultaneous users
3. **Large Datasets**: Verify performance with many records

## Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Verify SUPABASE_DB_URL format
   - Check database password
   - Ensure IP is allowlisted in Supabase

2. **Data Type Errors**:
   - Review PostgreSQL data type mappings
   - Check for unsupported SQLite extensions

3. **JSON Field Issues**:
   - Verify JSON structure is valid
   - Check for single quotes vs double quotes

4. **Foreign Key Violations**:
   - Ensure parent records exist before children
   - Check user_id references in internships

### Debug Commands

```cmd
# Test Supabase connection
python testsupabase.py

# Check migration logs
python migrate_to_supabase.py > migration.log 2>&1

# Verify specific table
python -c "from migrate_to_supabase import verify_table_data; verify_table_data('users')"
```

## Key Concepts Explained

### Database Indexes

**What are indexes?**
Indexes are database structures that improve query performance by creating shortcuts to data.

**When to use indexes:**
- Primary keys (automatic)
- Foreign keys (recommended)
- Frequently searched columns
- Columns used in WHERE clauses

**Our indexes:**
```sql
-- Automatically created for primary keys and unique constraints
-- Recommended additional indexes:
CREATE INDEX idx_internships_user_id ON internships(user_id);
CREATE INDEX idx_internships_status ON internships(status);
CREATE INDEX idx_internships_date_applied ON internships(date_applied);
CREATE INDEX idx_friendships_user_id ON friendships(user_id);
CREATE INDEX idx_friendships_friend_id ON friendships(friend_id);
```

### JSON Fields

**Advantages:**
- Store complex nested data
- Schema flexibility
- Native PostgreSQL support
- Indexable and queryable

**Our usage:**
- `contacts`: Array of contact objects
- `social_media`: Object with platform links

**Querying JSON:**
```sql
-- Find users with LinkedIn profiles
SELECT * FROM users WHERE social_media->>'linkedin' IS NOT NULL;

-- Find internships with specific contact roles
SELECT * FROM internships WHERE contacts @> '[{"role": "recruiter"}]';
```

### Row Level Security (RLS)

PostgreSQL feature for data access control:

```sql
-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE internships ENABLE ROW LEVEL SECURITY;

-- Create policies (example)
CREATE POLICY "Users can view own data" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can view own internships" ON internships
  FOR ALL USING (auth.uid() = user_id);
```

### ACID Compliance

PostgreSQL ensures ACID properties:
- **Atomicity**: Transactions are all-or-nothing
- **Consistency**: Database remains in valid state
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed data survives system failures

### Connection Pooling

For production deployment:
```python
# Configure connection pooling
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

## Next Steps

1. **Run Migration**: Execute the migration script
2. **Update Configuration**: Switch Flask to use PostgreSQL
3. **Test Thoroughly**: Verify all functionality works
4. **Deploy**: Consider production deployment options
5. **Monitor**: Set up database monitoring and backups
6. **Optimize**: Add indexes for better performance
7. **Security**: Implement Row Level Security if needed

## Rollback Plan

If issues arise:
1. Keep SQLite database as backup
2. Revert Flask configuration to SQLite
3. Address migration issues
4. Re-run migration with fixes

## Support Resources

- **Supabase Docs**: https://supabase.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **SQLAlchemy PostgreSQL**: https://docs.sqlalchemy.org/en/14/dialects/postgresql.html
- **Migration Best Practices**: Database-specific migration guides

---

**Created**: $(date)
**Version**: 1.0
**Author**: Migration Assistant
**Status**: Ready for execution
