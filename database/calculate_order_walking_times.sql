-- Function to calculate walking time for an order based on its items' bin locations
CREATE OR REPLACE FUNCTION calculate_order_walking_time(order_id_param INTEGER)
RETURNS DECIMAL AS $$
DECLARE
    total_walking_time DECIMAL := 0.0;
    bin_locations INTEGER[];
    from_bin_id INTEGER;
    to_bin_id INTEGER;
    walking_time DECIMAL;
    i INTEGER;
BEGIN
    -- Get all bin locations for items in this order
    -- Since SKUs don't have bin_id, we'll use a simplified approach
    -- For now, we'll use the SKU ID as a proxy for bin location
    SELECT ARRAY_AGG(DISTINCT s.id ORDER BY s.id)
    INTO bin_locations
    FROM order_items oi
    JOIN skus s ON oi.sku_id = s.id
    WHERE oi.order_id = order_id_param;
    
    -- If no items or only one item, return 0
    IF bin_locations IS NULL OR array_length(bin_locations, 1) <= 1 THEN
        RETURN 0.0;
    END IF;
    
    -- Calculate walking time between consecutive bins
    -- This is a simplified approach - in practice you'd want to optimize the route
    FOR i IN 1..array_length(bin_locations, 1) - 1 LOOP
        from_bin_id := bin_locations[i];
        to_bin_id := bin_locations[i + 1];
        
        -- Get walking time between these bins
        SELECT wt.walking_time_minutes
        INTO walking_time
        FROM walking_times wt
        WHERE wt.from_bin_id = from_bin_id 
        AND wt.to_bin_id = to_bin_id;
        
        -- If no walking time found, use a default (1 minute)
        IF walking_time IS NULL THEN
            walking_time := 1.0;
        END IF;
        
        total_walking_time := total_walking_time + walking_time;
    END LOOP;
    
    RETURN total_walking_time;
END;
$$ LANGUAGE plpgsql;

-- Function to get the number of items in an order
CREATE OR REPLACE FUNCTION get_order_item_count(order_id_param INTEGER)
RETURNS INTEGER AS $$
DECLARE
    item_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO item_count
    FROM order_items
    WHERE order_id = order_id_param;
    
    RETURN COALESCE(item_count, 0);
END;
$$ LANGUAGE plpgsql; 