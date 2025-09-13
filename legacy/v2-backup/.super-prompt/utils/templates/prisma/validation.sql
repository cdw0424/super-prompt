-- Validation queries (PostgreSQL-flavored) — adapt as needed.
-- 1) Orphaned orders (FK validation)
SELECT o.id FROM "Order" o
LEFT JOIN "User" u ON u.id = o.userId
WHERE u.id IS NULL
LIMIT 10;

-- 2) Duplicate user emails (UNIQUENESS)
SELECT email, COUNT(*)
FROM "User"
GROUP BY email
HAVING COUNT(*) > 1
LIMIT 10;

-- 3) Hot path performance (index candidates)
EXPLAIN ANALYZE
SELECT * FROM "Order"
WHERE userId = $1 AND createdAt >= now() - interval '30 days'
ORDER BY createdAt DESC
LIMIT 50;

