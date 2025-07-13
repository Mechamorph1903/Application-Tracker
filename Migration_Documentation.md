# SQLite to Supabase (PostgreSQL) Migration Guide

## Overview
This document explains the migration process from SQLite to Supabase PostgreSQL for the Flask Internship Tracker application. The migration includes schema translation, data transfer, and application configuration updates.

## Migration Progress

### ✅ Completed Steps

1. **Environment Setup**
   - Installed required dependencies: `python-dotenv`, `supabase`, `psycopg2-binary`
   - Created `.env` file with Supabase credentials
   - Set up Supabase project connection

2. **Schema Migration** 
   - Analyzed SQLite database schema using `app/models.py`
   - Created PostgreSQL table definitions in `create_supabase_tables.py`
   - Successfully created all tables in Supabase:
     - `user` - User accounts and profile information
     - `internship` - Internship applications and details
     - `friend_request` - Friend system relationships
     - `user_settings` - User preferences and configuration
   - Added appropriate indexes for performance
   - Verified table creation with SQL queries

3. **Data Migration Scripts**
   - Created comprehensive migration script (`migrate_to_supabase.py`)
   - Includes data type conversion (SQLite → PostgreSQL)
   - Handles JSON field migration (contacts, social_media)
   - Maps foreign key relationships correctly
   - Includes data verification and rollback capabilities

### 🔄 Current Status: Connection Issues

The migration script is ready but encountering PostgreSQL connection issues:
- Direct database connection to `db.yzrfoxjwqlthhmwvqguu.supabase.co` fails
- Hostname resolution errors suggest network or configuration issues
- Supabase REST API works correctly (confirmed via `testsupabase.py`)

## Database Schema Differences

### SQLite vs PostgreSQL Key Differences

1. **Data Types**
   - SQLite: Dynamic typing, stores everything as TEXT, INTEGER, REAL, or BLOB
   - PostgreSQL: Strict typing with specific types (VARCHAR, TIMESTAMP, JSONB, etc.)

2. **JSON Handling**
   - SQLite: Stores JSON as TEXT, requires manual parsing
   - PostgreSQL: Native JSONB support with indexing and querying capabilities

3. **Sequences and Auto-increment**
   - SQLite: Uses `AUTOINCREMENT` or `INTEGER PRIMARY KEY`
   - PostgreSQL: Uses `SERIAL` type and sequences (e.g., `user_id_seq`)

4. **Constraints**
   - SQLite: Limited constraint support
   - PostgreSQL: Full constraint support including CHECK, FOREIGN KEY, UNIQUE

## Schema Translation Details

### User Table
```sql
-- SQLite (original)
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName VARCHAR(50) NOT NULL,
    lastName VARCHAR(50) NOT NULL,
    -- ... other fields
);

-- PostgreSQL (Supabase)
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    "firstName" VARCHAR(50) NOT NULL,
    "lastName" VARCHAR(50) NOT NULL,
    -- ... other fields with proper types
);
```

### Key Changes Made:
1. **Reserved Keywords**: Quoted `"user"`, `"firstName"`, `"lastName"` due to PostgreSQL reserved words
2. **JSON Fields**: `social_media` and `contacts` converted to JSONB
3. **Timestamps**: Proper TIMESTAMP WITH TIME ZONE types
4. **Sequences**: Auto-increment handled by SERIAL and sequences

## Data Migration Process

### Migration Script Features (`migrate_to_supabase.py`)

1. **Connection Management**
   - SQLite connection with row factory for named access
   - PostgreSQL connection with proper error handling
   - Transaction management for data consistency

2. **Data Transformation**
   - JSON string parsing for contacts and social_media fields
   - Foreign key mapping (old IDs → new IDs)
   - Data type conversion and validation
   - Default value handling for new fields

3. **Migration Steps**
   ```python
   1. Verify tables exist in Supabase
   2. Clear existing data (with confirmation)
   3. Migrate users (returns ID mapping)
   4. Migrate internships (using user ID mapping)
   5. Migrate friend requests (using user ID mapping)
   6. Migrate user settings (using user ID mapping)
   7. Verify migration success
   ```

4. **Error Handling**
   - Database connection validation
   - Missing table detection
   - Foreign key relationship validation
   - Transaction rollback on errors

## Next Steps to Complete Migration

### Option 1: Resolve PostgreSQL Connection
1. **Check Supabase Project Settings**
   - Verify database URL in Supabase dashboard
   - Check if direct connections are enabled
   - Confirm IP restrictions or firewall settings

2. **Alternative Connection Methods**
   - Try pooler connection URL
   - Use connection pooling if available
   - Contact Supabase support for connection issues

### Option 2: Alternative Migration Approach
1. **CSV Export/Import**
   - Export SQLite data to CSV files
   - Use Supabase dashboard CSV import feature
   - Manual data verification

2. **Supabase REST API Migration**
   - Use Supabase Python client for data insertion
   - Batch insert operations for performance
   - Handle rate limiting and error retry

## Application Configuration Updates

### Flask App Changes Needed

1. **Database Configuration**
   ```python
   # Update app/__init__.py
   app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
   ```

2. **Environment Variables**
   ```bash
   # .env file
   SUPABASE_URL=https://yzrfoxjwqlthhmwvqguu.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   DATABASE_URL=postgresql://postgres:password@host:5432/postgres
   ```

3. **Model Updates** (if needed)
   - Verify column names match PostgreSQL schema
   - Update any SQLite-specific queries
   - Test JSON field access patterns

## Testing Strategy

### Post-Migration Verification

1. **Data Integrity Checks**
   - User count verification
   - Internship data completeness
   - Friend relationship validation
   - Settings preservation

2. **Application Testing**
   - User authentication flow
   - CRUD operations on internships
   - Friend system functionality
   - File upload/storage
   - Export functionality

3. **Performance Testing**
   - Query performance with PostgreSQL
   - Index utilization
   - JSON field querying

## Rollback Plan

### If Migration Issues Occur

1. **SQLite Backup**
   - Original database preserved in `instance/internships.db`
   - Backup files available: `instance/internships.db.backup_*`

2. **Configuration Rollback**
   - Switch back to SQLite in Flask configuration
   - Restore original environment variables

3. **Incremental Migration**
   - Migrate tables individually
   - Test each component separately
   - Validate data before proceeding

## Performance Considerations

### PostgreSQL Advantages

1. **Better JSON Support**
   - JSONB indexing for contacts and social_media
   - Native JSON operators and functions
   - Better query performance on JSON fields

2. **Concurrent Access**
   - Better handling of multiple users
   - Row-level locking
   - ACID compliance

3. **Scalability**
   - Horizontal scaling options
   - Connection pooling
   - Better resource management

## Security Improvements

### Supabase Security Features

1. **Row Level Security (RLS)**
   - Can be enabled for user data isolation
   - Fine-grained access control
   - Automatic security policy enforcement

2. **Connection Security**
   - SSL/TLS encryption by default
   - Connection pooling security
   - Credential management

## Monitoring and Maintenance

### Post-Migration Monitoring

1. **Database Performance**
   - Query execution times
   - Connection pool usage
   - Resource utilization

2. **Error Tracking**
   - Application error monitoring
   - Database connection issues
   - Query performance problems

## Contact Information

For migration support or questions:
- Review Supabase documentation: https://supabase.com/docs
- Check PostgreSQL migration guides
- Consult Flask-SQLAlchemy PostgreSQL documentation

---

**Migration Status**: Schema completed, data migration pending connection resolution
**Last Updated**: July 12, 2025
**Next Action**: Resolve PostgreSQL connection or implement alternative migration method
