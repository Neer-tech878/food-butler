# PostgreSQL Setup Guide for Food Butler

## Current Situation
The Food Butler backend requires PostgreSQL to be running on port 5432.

## Option 1: Start Docker Desktop (RECOMMENDED)

1. **Open Docker Desktop app** on your Mac
2. **Wait for it to fully start** (whale icon should be steady, not animated)
3. **Run this command**:
   ```bash
   cd /Users/jaswanthyamana/food_butler_platform
   ./start_with_docker_db.sh
   ```

This will:
- Start PostgreSQL in a Docker container
- Start the backend API
- Make the admin panel ready for login

## Option 2: Install and Start PostgreSQL via Homebrew

```bash
# Install PostgreSQL
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install postgresql@14

# Initialize database
initdb /usr/local/var/postgresql@14

# Start PostgreSQL
postgres -D /usr/local/var/postgresql@14
```

Then in a new terminal:
```bash
cd /Users/jaswanthyamana/food_butler_platform/food_butler_backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Option 3: Use Postgres.app

1. **Download**: https://postgresapp.com/
2. **Install and open** Postgres.app
3. **Click "Initialize"** to create a new server
4. **Start the server**
5. **Update connection settings** in `.env`:
   ```
   DATABASE_URL="postgresql://your_username@localhost/food_butler_db"
   ```
6. **Create the database**:
   ```bash
   psql -U your_username -c "CREATE DATABASE food_butler_db;"
   ```
7. **Start the backend**:
   ```bash
   cd food_butler_backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## After Database is Running

Once PostgreSQL is running, you can login to the admin panel:

- **URL**: http://127.0.0.1:5500/frontend/admin.html
- **Email**: admin@foodbutler.com
- **Password**: admin123

## Troubleshooting

### Check if PostgreSQL is running:
```bash
nc -zv localhost 5432
# Should show: Connection to localhost port 5432 [tcp/postgresql] succeeded!
```

### Check backend logs:
```bash
tail -f food_butler_backend/backend.log
```

### Restart everything:
```bash
# Kill backend
lsof -ti:8000 | xargs kill -9

# If using Docker:
docker compose -f docker-compose.db-only.yml restart

# Restart backend
cd food_butler_backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
