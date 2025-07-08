-- Add bin_id foreign key to skus table
ALTER TABLE skus ADD COLUMN IF NOT EXISTS bin_id INTEGER REFERENCES bins(id);

-- (Optional) Link sample SKUs to bins (assuming 1:1 for demo)
UPDATE skus SET bin_id = (SELECT id FROM bins WHERE bin_id = 'BIN001') WHERE sku_code = 'SKU001';
UPDATE skus SET bin_id = (SELECT id FROM bins WHERE bin_id = 'BIN002') WHERE sku_code = 'SKU002';
UPDATE skus SET bin_id = (SELECT id FROM bins WHERE bin_id = 'BIN003') WHERE sku_code = 'SKU003';
UPDATE skus SET bin_id = (SELECT id FROM bins WHERE bin_id = 'BIN004') WHERE sku_code = 'SKU004';
UPDATE skus SET bin_id = (SELECT id FROM bins WHERE bin_id = 'BIN005') WHERE sku_code = 'SKU005';
UPDATE skus SET bin_id = (SELECT id FROM bins WHERE bin_id = 'BIN006') WHERE sku_code = 'SKU006';
UPDATE skus SET bin_id = (SELECT id FROM bins WHERE bin_id = 'BIN007') WHERE sku_code = 'SKU007';
UPDATE skus SET bin_id = (SELECT id FROM bins WHERE bin_id = 'BIN008') WHERE sku_code = 'SKU008';
UPDATE skus SET bin_id = (SELECT id FROM bins WHERE bin_id = 'BIN009') WHERE sku_code = 'SKU009';
UPDATE skus SET bin_id = (SELECT id FROM bins WHERE bin_id = 'BIN010') WHERE sku_code = 'SKU010';

-- Make bin_id NOT NULL if every SKU is assigned
-- ALTER TABLE skus ALTER COLUMN bin_id SET NOT NULL;

-- Create index for the foreign key
CREATE INDEX IF NOT EXISTS idx_skus_bin_id ON skus(bin_id); 