
-- Daily deadline update script
-- Run this script daily to keep order deadlines in the future

UPDATE orders 
SET shipping_deadline = shipping_deadline + INTERVAL '1 day'
WHERE shipping_deadline < NOW() + INTERVAL '1 day';

-- Optional: Add some randomness to deadlines within the day
UPDATE orders 
SET shipping_deadline = shipping_deadline + (RANDOM() * INTERVAL '12 hours')
WHERE shipping_deadline::date = CURRENT_DATE + INTERVAL '1 day';
