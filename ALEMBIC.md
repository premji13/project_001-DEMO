# Database Migrations with Alembic

## Overview
Alembic is a lightweight database migration tool for SQLAlchemy. It allows you to manage database schema changes over time in a version-controlled manner.

## Setup

Alembic has already been initialized in the project. The migration environment is located in the `alembic/` directory.

## Key Files

- **alembic.ini** - Configuration file (database URL should match your environment)
- **alembic/env.py** - Python environment script that sets up migrations
- **alembic/versions/** - Directory containing migration scripts
- **alembic/script.py.mako** - Template for generating new migrations

## Common Commands

### Create a New Migration

**Auto-generate (Recommended):**
```bash
alembic revision --autogenerate -m "Description of changes"
```

This automatically detects changes in your SQLAlchemy models and creates a migration.

**Manual Migration:**
```bash
alembic revision -m "Description of changes"
```

This creates an empty migration that you can edit manually.

### Apply Migrations

**Upgrade to Latest:**
```bash
alembic upgrade head
```

**Upgrade to Specific Revision:**
```bash
alembic upgrade 47f25e6fe597
```

**Downgrade One Step:**
```bash
alembic downgrade -1
```

**Downgrade to Specific Revision:**
```bash
alembic downgrade 47f25e6fe597
```

### View Migration Status

```bash
alembic current      # Show current database version
alembic history      # Show all migrations
alembic branches     # Show branch information
```

## Migration Workflow

### 1. Make Model Changes
Edit your SQLAlchemy models in `app/models.py`:

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    phone = Column(String)  # New field
```

### 2. Generate Migration
```bash
alembic revision --autogenerate -m "Add phone field to users"
```

Review the generated migration file in `alembic/versions/`.

### 3. Apply Migration
```bash
alembic upgrade head
```

### 4. Commit Changes
```bash
git add alembic/versions/
git commit -m "Migration: Add phone field to users"
```

## Migration File Structure

Each migration file contains two functions:

```python
def upgrade() -> None:
    """Apply the migration (move forward in time)"""
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))

def downgrade() -> None:
    """Revert the migration (move backward in time)"""
    op.drop_column('users', 'phone')
```

## Current Migrations

### 47f25e6fe597 - Initial migration: create users table
- Creates the `users` table with columns:
  - id (Integer, Primary Key)
  - email (String, Unique)
  - username (String, Unique)
  - hashed_password (String)
  - is_active (Boolean, default: True)
  - is_verified (Boolean, default: False)
  - created_at (DateTime)
  - updated_at (DateTime)

## Best Practices

1. **Auto-generate migrations** - Let Alembic detect changes automatically
2. **Review migrations** - Always review generated migrations before applying
3. **Test migrations** - Test both upgrade and downgrade in development
4. **One change per migration** - Keep migrations focused and clear
5. **Descriptive names** - Use clear, descriptive migration messages
6. **Version control** - Always commit migration files to git
7. **Never modify applied migrations** - Create new migrations for changes

## Troubleshooting

### Migration not detected
- Ensure models are imported in `alembic/env.py`
- Check that `target_metadata` is correctly set
- Verify changes are in model definitions, not in instance

### Database connection error
- Check DATABASE_URL in .env file
- Ensure PostgreSQL is running
- Verify credentials are correct

### Revision conflict
- Two developers may create conflicting migrations
- Solution: Merge them manually or use `alembic merge`
  ```bash
  alembic merge -m "Merge migration branches"
  ```

## Integration with Startup

The application automatically creates tables on startup if they don't exist:

```python
# app/main.py
@app.on_event("startup")
async def startup():
    init_db()  # Creates all tables from models
```

For production, use migrations instead:
```bash
alembic upgrade head
```

## Environment Variables

Alembic uses `DATABASE_URL` from your `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost:5432/demo_db
```

Update this in `.env` before running migrations.
