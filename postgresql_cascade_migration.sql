
-- PostgreSQL CASCADE DELETE Migration
-- Run this in Render Shell or PostgreSQL console

BEGIN;

-- Add CASCADE DELETE to friend_request table
ALTER TABLE friend_request 
DROP CONSTRAINT IF EXISTS friend_request_requester_id_fkey;

ALTER TABLE friend_request 
DROP CONSTRAINT IF EXISTS friend_request_addressee_id_fkey;

ALTER TABLE friend_request 
ADD CONSTRAINT friend_request_requester_id_fkey 
FOREIGN KEY (requester_id) REFERENCES users (id) ON DELETE CASCADE;

ALTER TABLE friend_request 
ADD CONSTRAINT friend_request_addressee_id_fkey 
FOREIGN KEY (addressee_id) REFERENCES users (id) ON DELETE CASCADE;

-- Add CASCADE DELETE to internship table
ALTER TABLE internship 
DROP CONSTRAINT IF EXISTS internship_user_id_fkey;

ALTER TABLE internship 
ADD CONSTRAINT internship_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;

COMMIT;

-- Verify constraints
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    tc.constraint_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND tc.table_name IN ('friend_request', 'internship');
