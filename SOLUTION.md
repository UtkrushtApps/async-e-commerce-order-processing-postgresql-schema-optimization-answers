# Solution Steps

1. Define the normalized SQLAlchemy models in 'models.py', using ForeignKey constraints for referential integrity, relationship()s for ORM navigation, and add indexes for commonly queried fields (user_id, status, created_at, etc).

2. In 'database.py', set up SQLAlchemy's async engine and sessionmaker pointing to the PostgreSQL database using asyncpg, making sure sessions are compatible with async/await.

3. Design Pydantic schemas for users, products, order creation, order responses, and order items in 'schemas.py' for clean and type-safe FastAPI endpoint payloads/responses.

4. Develop async CRUD logic in 'crud.py': use async SQLAlchemy queries (select, update, etc), enforce transaction safety using async with db.begin(), select products with .with_for_update() to prevent race conditions, and handle validation for stock and input data.

5. Implement order archiving in 'crud.py' using an async query that updates status for completed orders older than N days, with safe commit.

6. Build endpoints in 'main.py' using FastAPI for listing, creating, retrieving, and completing products/orders, and wire up the CRUD functions with proper error handling and dependency injection for the async DB session.

7. Add a startup event in 'main.py' to run Base.metadata.create_all to auto-create tables (for demo) and to launch a coroutine background task that periodically calls the async archiver logic.

8. In the background archiver, create a loop that uses an async DB session and calls the archive_old_orders function every hour, handling all exceptions gracefully.

9. Test core logic by placing orders, completing them, and ensuring older completed orders are archived asynchronously without blocking any normal API endpoint.

