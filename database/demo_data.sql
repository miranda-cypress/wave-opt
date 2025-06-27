-- Demo Data for AI Wave Optimization Agent
-- Populates the database with realistic warehouse data

-- Insert warehouse
INSERT INTO warehouses (name, total_sqft, zones, shift_start_hour, shift_end_hour, max_orders_per_day, deadline_penalty_per_hour, overtime_multiplier) 
VALUES ('MidWest Distribution Co', 85000, 5, 6, 22, 2500, 100.00, 1.50);

-- Insert workers with varying skills and efficiency
INSERT INTO workers (warehouse_id, name, hourly_rate, efficiency_factor, max_hours_per_day) VALUES
-- Multi-skilled workers (efficient)
(1, 'Sarah Johnson', 24.00, 1.15, 8.00),
(1, 'Mike Chen', 22.00, 1.10, 8.00),
(1, 'Lisa Rodriguez', 23.00, 1.12, 8.00),
(1, 'David Kim', 21.00, 1.08, 8.00),
(1, 'Emma Wilson', 25.00, 1.18, 8.00),

-- Specialized workers (less efficient)
(1, 'James Thompson', 18.00, 0.95, 8.00),
(1, 'Maria Garcia', 19.00, 0.98, 8.00),
(1, 'Robert Lee', 20.00, 1.02, 8.00),
(1, 'Jennifer Davis', 17.00, 0.92, 8.00),
(1, 'Christopher Brown', 19.50, 1.00, 8.00),

-- Mixed skill workers
(1, 'Amanda Miller', 21.50, 1.05, 8.00),
(1, 'Daniel Martinez', 20.50, 1.03, 8.00),
(1, 'Jessica Taylor', 22.50, 1.07, 8.00),
(1, 'Kevin Anderson', 21.00, 1.01, 8.00),
(1, 'Nicole White', 23.50, 1.09, 8.00);

-- Insert worker skills
-- Sarah Johnson - Multi-skilled
INSERT INTO worker_skills (worker_id, skill_type) VALUES (1, 'picking'), (1, 'packing'), (1, 'shipping');

-- Mike Chen - Multi-skilled
INSERT INTO worker_skills (worker_id, skill_type) VALUES (2, 'picking'), (2, 'consolidation'), (2, 'staging');

-- Lisa Rodriguez - Multi-skilled
INSERT INTO worker_skills (worker_id, skill_type) VALUES (3, 'packing'), (3, 'labeling'), (3, 'shipping');

-- David Kim - Multi-skilled
INSERT INTO worker_skills (worker_id, skill_type) VALUES (4, 'picking'), (4, 'packing'), (4, 'consolidation');

-- Emma Wilson - Multi-skilled
INSERT INTO worker_skills (worker_id, skill_type) VALUES (5, 'packing'), (5, 'labeling'), (5, 'shipping');

-- James Thompson - Specialized
INSERT INTO worker_skills (worker_id, skill_type) VALUES (6, 'picking');

-- Maria Garcia - Specialized
INSERT INTO worker_skills (worker_id, skill_type) VALUES (7, 'packing');

-- Robert Lee - Specialized
INSERT INTO worker_skills (worker_id, skill_type) VALUES (8, 'shipping');

-- Jennifer Davis - Specialized
INSERT INTO worker_skills (worker_id, skill_type) VALUES (9, 'labeling');

-- Christopher Brown - Specialized
INSERT INTO worker_skills (worker_id, skill_type) VALUES (10, 'consolidation');

-- Amanda Miller - Mixed skills
INSERT INTO worker_skills (worker_id, skill_type) VALUES (11, 'picking'), (11, 'packing');

-- Daniel Martinez - Mixed skills
INSERT INTO worker_skills (worker_id, skill_type) VALUES (12, 'packing'), (12, 'labeling');

-- Jessica Taylor - Mixed skills
INSERT INTO worker_skills (worker_id, skill_type) VALUES (13, 'shipping'), (13, 'staging');

-- Kevin Anderson - Mixed skills
INSERT INTO worker_skills (worker_id, skill_type) VALUES (14, 'picking'), (14, 'consolidation');

-- Nicole White - Mixed skills
INSERT INTO worker_skills (worker_id, skill_type) VALUES (15, 'labeling'), (15, 'shipping');

-- Insert equipment
INSERT INTO equipment (warehouse_id, name, equipment_type, capacity, hourly_cost, efficiency_factor) VALUES
-- Packing stations (bottleneck equipment)
(1, 'Packing Station 1', 'packing_station', 1, 15.00, 1.05),
(1, 'Packing Station 2', 'packing_station', 1, 15.00, 1.02),
(1, 'Packing Station 3', 'packing_station', 1, 15.00, 0.98),
(1, 'Packing Station 4', 'packing_station', 1, 15.00, 1.08),
(1, 'Packing Station 5', 'packing_station', 1, 15.00, 1.01),
(1, 'Packing Station 6', 'packing_station', 1, 15.00, 0.95),
(1, 'Packing Station 7', 'packing_station', 1, 15.00, 1.03),
(1, 'Packing Station 8', 'packing_station', 1, 15.00, 1.06),

-- Dock doors (shipping bottleneck)
(1, 'Dock Door 1', 'dock_door', 1, 5.00, 1.00),
(1, 'Dock Door 2', 'dock_door', 1, 5.00, 1.00),
(1, 'Dock Door 3', 'dock_door', 1, 5.00, 1.00),
(1, 'Dock Door 4', 'dock_door', 1, 5.00, 1.00),
(1, 'Dock Door 5', 'dock_door', 1, 5.00, 1.00),
(1, 'Dock Door 6', 'dock_door', 1, 5.00, 1.00),

-- Pick carts
(1, 'Pick Cart 1', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 2', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 3', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 4', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 5', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 6', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 7', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 8', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 9', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 10', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 11', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 12', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 13', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 14', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 15', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 16', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 17', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 18', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 19', 'pick_cart', 1, 2.00, 1.00),
(1, 'Pick Cart 20', 'pick_cart', 1, 2.00, 1.00),

-- Conveyors
(1, 'Conveyor 1', 'conveyor', 5, 8.00, 1.00),
(1, 'Conveyor 2', 'conveyor', 5, 8.00, 1.00),
(1, 'Conveyor 3', 'conveyor', 5, 8.00, 1.00),

-- Label printers
(1, 'Label Printer 1', 'label_printer', 1, 3.00, 1.00),
(1, 'Label Printer 2', 'label_printer', 1, 3.00, 1.00),
(1, 'Label Printer 3', 'label_printer', 1, 3.00, 1.00),
(1, 'Label Printer 4', 'label_printer', 1, 3.00, 1.00);

-- Insert SKUs with Pareto distribution (80/15/5 rule)
-- Electronics (Zone 1)
INSERT INTO skus (warehouse_id, name, zone, pick_time_minutes, pack_time_minutes, volume_cubic_feet, weight_lbs) VALUES
(1, 'Laptop Pro 15"', 1, 3.5, 4.2, 2.5, 4.8),
(1, 'Laptop Pro 13"', 1, 3.2, 3.8, 2.1, 3.9),
(1, 'Smartphone X', 1, 2.8, 3.1, 0.8, 0.4),
(1, 'Tablet Air', 1, 3.0, 3.5, 1.2, 1.1),
(1, 'Wireless Headphones', 1, 2.5, 2.8, 0.6, 0.3),
(1, 'USB-C Charger', 1, 1.8, 2.0, 0.3, 0.2),
(1, 'Bluetooth Speaker', 1, 2.9, 3.3, 1.5, 1.8),
(1, 'Gaming Mouse', 1, 2.2, 2.5, 0.4, 0.3),
(1, 'Mechanical Keyboard', 1, 2.7, 3.0, 1.8, 2.1),
(1, 'Monitor 27"', 1, 4.2, 5.0, 8.5, 12.3);

-- Clothing (Zone 2)
INSERT INTO skus (warehouse_id, name, zone, pick_time_minutes, pack_time_minutes, volume_cubic_feet, weight_lbs) VALUES
(1, 'Cotton T-Shirt L', 2, 2.1, 2.3, 0.8, 0.4),
(1, 'Denim Jeans 32x32', 2, 2.5, 2.8, 1.2, 1.1),
(1, 'Wool Sweater M', 2, 2.8, 3.2, 1.5, 0.8),
(1, 'Leather Jacket L', 2, 3.2, 3.8, 2.8, 3.2),
(1, 'Running Shoes 10', 2, 2.9, 3.1, 1.8, 1.5),
(1, 'Hoodie XL', 2, 2.4, 2.6, 1.1, 0.7),
(1, 'Dress Shirt M', 2, 2.6, 2.9, 0.9, 0.5),
(1, 'Winter Coat L', 2, 3.5, 4.0, 3.2, 4.1),
(1, 'Athletic Shorts M', 2, 2.0, 2.2, 0.6, 0.3),
(1, 'Socks Pack 6', 2, 1.8, 2.0, 0.4, 0.2);

-- Home (Zone 3)
INSERT INTO skus (warehouse_id, name, zone, pick_time_minutes, pack_time_minutes, volume_cubic_feet, weight_lbs) VALUES
(1, 'Table Lamp Modern', 3, 3.8, 4.5, 3.2, 2.8),
(1, 'Office Chair Ergonomic', 3, 4.5, 5.2, 12.5, 18.7),
(1, 'Coffee Table Wood', 3, 4.2, 4.8, 8.9, 15.2),
(1, 'Wall Mirror Round', 3, 3.5, 4.0, 2.8, 3.1),
(1, 'Area Rug 8x10', 3, 4.8, 5.5, 15.2, 8.9),
(1, 'Throw Pillow Decorative', 3, 2.2, 2.5, 0.8, 0.6),
(1, 'Desk Lamp LED', 3, 3.2, 3.7, 2.1, 1.8),
(1, 'Bookshelf 5-Shelf', 3, 4.0, 4.6, 10.5, 12.8),
(1, 'Bedside Table', 3, 3.6, 4.1, 4.2, 6.5),
(1, 'Floor Vase Ceramic', 3, 3.4, 3.9, 3.8, 4.2);

-- Sports (Zone 4)
INSERT INTO skus (warehouse_id, name, zone, pick_time_minutes, pack_time_minutes, volume_cubic_feet, weight_lbs) VALUES
(1, 'Basketball Official', 4, 2.8, 3.1, 1.5, 1.2),
(1, 'Tennis Racket Pro', 4, 3.1, 3.4, 2.8, 0.9),
(1, 'Yoga Mat Premium', 4, 2.5, 2.8, 1.2, 0.8),
(1, 'Dumbbells 20lb Pair', 4, 3.8, 4.2, 3.5, 20.0),
(1, 'Mountain Bike 26"', 4, 5.2, 6.0, 25.8, 32.5),
(1, 'Treadmill Electric', 4, 6.5, 7.2, 45.2, 89.7),
(1, 'Weight Bench Adjustable', 4, 4.8, 5.3, 12.8, 18.5),
(1, 'Golf Clubs Set', 4, 4.2, 4.7, 8.5, 12.8),
(1, 'Soccer Ball Size 5', 4, 2.6, 2.9, 1.8, 1.1),
(1, 'Swimming Goggles', 4, 2.1, 2.3, 0.3, 0.2);

-- Books (Zone 5)
INSERT INTO skus (warehouse_id, name, zone, pick_time_minutes, pack_time_minutes, volume_cubic_feet, weight_lbs) VALUES
(1, 'Novel Bestseller', 5, 1.8, 2.0, 0.6, 0.8),
(1, 'Textbook Calculus', 5, 2.2, 2.4, 1.2, 2.1),
(1, 'Magazine Monthly', 5, 1.5, 1.7, 0.4, 0.3),
(1, 'Cookbook Recipes', 5, 2.0, 2.2, 0.8, 1.2),
(1, 'Journal Hardcover', 5, 1.9, 2.1, 0.7, 0.9),
(1, 'Children Book Illustrated', 5, 1.7, 1.9, 0.5, 0.6),
(1, 'Reference Dictionary', 5, 2.3, 2.5, 1.5, 2.8),
(1, 'Poetry Collection', 5, 1.6, 1.8, 0.4, 0.5),
(1, 'Biography Hardcover', 5, 2.1, 2.3, 0.9, 1.4),
(1, 'Self-Help Paperback', 5, 1.8, 2.0, 0.6, 0.7);

-- Insert customers
INSERT INTO customers (name, email, phone) VALUES
('Acme Corporation', 'orders@acme.com', '555-0101'),
('TechStart Inc', 'purchasing@techstart.com', '555-0102'),
('Global Retail Co', 'orders@globalretail.com', '555-0103'),
('Local Store Chain', 'inventory@localstore.com', '555-0104'),
('Online Marketplace', 'fulfillment@onlinemarket.com', '555-0105'),
('University Bookstore', 'textbooks@university.edu', '555-0106'),
('Sports Equipment Plus', 'orders@sportsequipment.com', '555-0107'),
('Home Decor Outlet', 'sales@homedecor.com', '555-0108'),
('Fashion Forward', 'orders@fashionforward.com', '555-0109'),
('Electronics Hub', 'purchasing@electronicshub.com', '555-0110');

-- Insert orders with realistic deadlines and priorities
-- High priority orders (deadline pressure scenario)
INSERT INTO orders (warehouse_id, customer_id, priority, shipping_deadline, total_pick_time, total_pack_time, total_volume, total_weight, status) VALUES
(1, 1, '1', NOW() + INTERVAL '2 hours', 15.5, 18.2, 12.8, 8.5, 'pending'),
(1, 2, '1', NOW() + INTERVAL '3 hours', 12.8, 14.5, 8.9, 6.2, 'pending'),
(1, 3, '1', NOW() + INTERVAL '4 hours', 18.2, 21.5, 15.2, 12.8, 'pending'),
(1, 4, '1', NOW() + INTERVAL '2.5 hours', 14.1, 16.8, 10.5, 7.8, 'pending'),
(1, 5, '1', NOW() + INTERVAL '3.5 hours', 16.7, 19.3, 13.1, 9.4, 'pending');

-- Medium priority orders (bottleneck scenario)
INSERT INTO orders (warehouse_id, customer_id, priority, shipping_deadline, total_pick_time, total_pack_time, total_volume, total_weight, status) VALUES
(1, 6, '3', NOW() + INTERVAL '6 hours', 22.5, 28.1, 18.9, 15.2, 'pending'),
(1, 7, '3', NOW() + INTERVAL '7 hours', 19.8, 24.5, 16.3, 12.1, 'pending'),
(1, 8, '3', NOW() + INTERVAL '8 hours', 25.3, 31.2, 21.7, 18.9, 'pending'),
(1, 9, '3', NOW() + INTERVAL '6.5 hours', 20.1, 25.8, 17.2, 13.5, 'pending'),
(1, 10, '3', NOW() + INTERVAL '7.5 hours', 23.7, 29.4, 19.8, 16.7, 'pending'),
(1, 1, '3', NOW() + INTERVAL '8.5 hours', 21.4, 26.9, 18.1, 14.3, 'pending'),
(1, 2, '3', NOW() + INTERVAL '9 hours', 24.8, 30.5, 20.5, 17.8, 'pending'),
(1, 3, '3', NOW() + INTERVAL '9.5 hours', 18.9, 23.7, 15.6, 11.9, 'pending'),
(1, 4, '3', NOW() + INTERVAL '10 hours', 26.2, 32.1, 22.8, 19.5, 'pending'),
(1, 5, '3', NOW() + INTERVAL '10.5 hours', 17.6, 22.3, 14.7, 10.8, 'pending');

-- Low priority orders (inefficient scenario)
INSERT INTO orders (warehouse_id, customer_id, priority, shipping_deadline, total_pick_time, total_pack_time, total_volume, total_weight, status) VALUES
(1, 6, '5', NOW() + INTERVAL '12 hours', 28.9, 35.6, 24.3, 21.7, 'pending'),
(1, 7, '5', NOW() + INTERVAL '13 hours', 31.2, 38.9, 26.8, 24.1, 'pending'),
(1, 8, '5', NOW() + INTERVAL '14 hours', 27.5, 33.8, 23.1, 20.4, 'pending'),
(1, 9, '5', NOW() + INTERVAL '15 hours', 29.8, 36.5, 25.6, 22.9, 'pending'),
(1, 10, '5', NOW() + INTERVAL '16 hours', 32.1, 39.2, 27.9, 25.3, 'pending');

-- Insert order items (sample items for each order)
-- High priority orders
INSERT INTO order_items (order_id, sku_id, quantity) VALUES
(1, 1, 2), (1, 5, 1), (1, 8, 3),  -- Electronics order
(2, 11, 4), (2, 15, 2), (2, 18, 1), -- Clothing order
(3, 21, 1), (3, 25, 3), (3, 28, 2), -- Home order
(4, 31, 2), (4, 35, 1), (4, 38, 4), -- Sports order
(5, 41, 3), (5, 45, 2), (5, 48, 1); -- Books order

-- Medium priority orders
INSERT INTO order_items (order_id, sku_id, quantity) VALUES
(6, 2, 3), (6, 6, 2), (6, 9, 1), (6, 12, 4),
(7, 16, 2), (7, 19, 3), (7, 22, 1), (7, 26, 2),
(8, 32, 1), (8, 36, 2), (8, 39, 3), (8, 42, 1),
(9, 7, 2), (9, 13, 1), (9, 17, 3), (9, 23, 2),
(10, 27, 2), (10, 33, 1), (10, 37, 2), (10, 43, 3),
(11, 3, 1), (11, 10, 2), (11, 14, 3), (11, 20, 1),
(12, 24, 2), (12, 29, 1), (12, 34, 2), (12, 40, 3),
(13, 4, 3), (13, 11, 1), (13, 18, 2), (13, 25, 1),
(14, 30, 1), (14, 35, 2), (14, 41, 3), (14, 46, 1),
(15, 8, 2), (15, 15, 1), (15, 21, 2), (15, 28, 3);

-- Low priority orders
INSERT INTO order_items (order_id, sku_id, quantity) VALUES
(16, 1, 4), (16, 6, 3), (16, 12, 2), (16, 19, 1), (16, 26, 3),
(17, 31, 2), (17, 37, 4), (17, 43, 1), (17, 47, 2), (17, 50, 3),
(18, 5, 1), (18, 11, 3), (18, 17, 2), (18, 23, 4), (18, 29, 1),
(19, 33, 3), (19, 39, 1), (19, 45, 2), (19, 49, 3), (19, 2, 1),
(20, 7, 2), (20, 13, 4), (20, 20, 1), (20, 27, 3), (20, 34, 2);

-- Insert sample optimization run
INSERT INTO optimization_runs (warehouse_id, name, description, status, optimization_horizon_hours, time_limit_seconds, started_at, completed_at, solver_status, optimization_runtime_seconds, total_orders, total_workers, total_equipment, total_cost, total_labor_cost, total_equipment_cost, total_deadline_penalties, on_time_percentage) VALUES
(1, 'Demo Bottleneck Scenario', 'Equipment bottleneck optimization with 50 orders', 'completed', 16, 600, NOW() - INTERVAL '1 hour', NOW() - INTERVAL '30 minutes', 'FEASIBLE', 10.21, 50, 15, 41, 785.83, 785.83, 0.00, 0.00, 100.00); 