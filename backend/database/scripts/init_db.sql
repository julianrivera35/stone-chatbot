CREATE OR REPLACE FUNCTION populate_database() RETURNS void AS $$
DECLARE
    user_id INT;
    customer_id INT;
BEGIN

    -- Insert categories
    INSERT INTO database_category (name, parent_id)
    SELECT 'Category 1', NULL
    WHERE NOT EXISTS (SELECT 1 FROM database_category WHERE name = 'Category 1');

    INSERT INTO database_category (name, parent_id)
    SELECT 'Category 2', NULL
    WHERE NOT EXISTS (SELECT 1 FROM database_category WHERE name = 'Category 2');

    INSERT INTO database_category (name, parent_id)
    SELECT 'Category 3', NULL
    WHERE NOT EXISTS (SELECT 1 FROM database_category WHERE name = 'Category 3');

    INSERT INTO database_category (name, parent_id)
    SELECT 'Category 4', NULL
    WHERE NOT EXISTS (SELECT 1 FROM database_category WHERE name = 'Category 4');

    INSERT INTO database_category (name, parent_id)
    SELECT 'Category 5', 3
    WHERE NOT EXISTS (SELECT 1 FROM database_category WHERE name = 'Category 5');

    -- Insert brands
    INSERT INTO database_brand (name)
    SELECT 'Brand 1'
    WHERE NOT EXISTS (SELECT 1 FROM database_brand WHERE name = 'Brand 1');

    INSERT INTO database_brand (name)
    SELECT 'Brand 2'
    WHERE NOT EXISTS (SELECT 1 FROM database_brand WHERE name = 'Brand 2');

    INSERT INTO database_brand (name)
    SELECT 'Brand 3'
    WHERE NOT EXISTS (SELECT 1 FROM database_brand WHERE name = 'Brand 3');

    INSERT INTO database_brand (name)
    SELECT 'Samsung'
    WHERE NOT EXISTS (SELECT 1 FROM database_brand WHERE name = 'Samsung');
    
    INSERT INTO database_brand (name)
    SELECT 'Apple'
    WHERE NOT EXISTS (SELECT 1 FROM database_brand WHERE name = 'Apple');

    -- Insert products
    INSERT INTO database_product (name, description, category_id, brand_id, price, specifications, stock, image_url, created_at, updated_at)
    SELECT 'Product 1', 'Product 1 description',
            (SELECT id FROM database_category WHERE name = 'Category 1'),
            (SELECT id FROM database_brand WHERE name = 'Brand 1'),
            10000,
            '{"specification1": "value1", "specification2": "value2", "specification3": "value3"}'::jsonb, 
            10, '', NOW(), NOW()
    WHERE NOT EXISTS (SELECT 1 FROM database_product WHERE name = 'Product 1');

    INSERT INTO database_product (name, description, category_id, brand_id, price, specifications, stock, image_url, created_at, updated_at)
    SELECT 'Product 2', 'Product 2 description',
            (SELECT id FROM database_category WHERE name = 'Category 2'),
            (SELECT id FROM database_brand WHERE name = 'Brand 2'),
            20000,
            '{"specification1": "value1", "specification2": "value2", "specification3": "value3"}'::jsonb,
            20, '', NOW(), NOW()
    WHERE NOT EXISTS (SELECT 1 FROM database_product WHERE name = 'Product 2');

    INSERT INTO database_product (name, description, category_id, brand_id, price, specifications, stock, image_url, created_at, updated_at)
    SELECT 'Product 3', 'Product 3 description',
            (SELECT id FROM database_category WHERE name = 'Category 3'),
            (SELECT id FROM database_brand WHERE name = 'Brand 3'),
            30000,
            '{"display": "6.1-inch Liquid Retina HD display", "chip": "A14 Bionic chip", "camera": "12MP Wide camera, 12MP Ultra Wide camera", "storage": "64GB, 128GB, 256GB", "battery": "2815mAh", "connector": "Lightning connector", "OS": "iOS 14"}'::jsonb, 
            30, '', NOW(), NOW()
    WHERE NOT EXISTS (SELECT 1 FROM database_product WHERE name = 'Product 3');

    INSERT INTO database_product (name, description, category_id, brand_id, price, specifications, stock, image_url, created_at, updated_at)
    SELECT 'Samsung Galaxy S21', 'Samsung Galaxy S21 description',
            (SELECT id FROM database_category WHERE name = 'Category 4'),
            (SELECT id FROM database_brand WHERE name = 'Samsung'),
            40000,
            '{"display": "6.2-inch Dynamic AMOLED 2X", "chip": "Exynos 2100", "camera": "12MP Wide camera, 12MP Ultra Wide camera, 64MP Telephoto camera", "storage": "128GB, 256GB", "battery": "4000mAh", "connector": "USB-C connector", "OS": "Android 11"}'::jsonb, 
            40, '', NOW(), NOW()
    WHERE NOT EXISTS (SELECT 1 FROM database_product WHERE name = 'Product 4');

    INSERT INTO database_product (name, description, category_id, brand_id, price, specifications, stock, image_url, created_at, updated_at)
    SELECT 'iPad Pro', 'iPad Pro description',
            (SELECT id FROM database_category WHERE name = 'Category 5'),
            (SELECT id FROM database_brand WHERE name = 'Apple'),
            50000, 
            '{"display": "12.9-inch Liquid Retina XDR display", "chip": "Apple M1 chip", "camera": "12MP Wide camera, 10MP Ultra Wide camera, LiDAR Scanner", "storage": "128GB, 256GB, 512GB, 1TB, 2TB", "battery": "40.88-watt-hour rechargeable lithium-polymer battery", "connector": "USB-C connector", "OS": "iPadOS 14"}'::jsonb,
            50, '', NOW(), NOW()
    WHERE NOT EXISTS (SELECT 1 FROM database_product WHERE name = 'Product 5');

    -- Insert users
    IF NOT EXISTS (SELECT 1 FROM database_customer WHERE email = 'test_user@example.com') THEN
        INSERT INTO database_customer(email, password, first_name, last_name, role, is_active, is_staff, is_superuser, created_at, date_of_birth, date_joined)
        VALUES ('test@example.com', 'Testpassword1234*', 'Test', 'User', 'Customer', TRUE, FALSE, FALSE, NOW(), '2000-01-01', NOW())
        RETURNING id INTO user_id;
    ELSE
        SELECT id INTO user_id FROM database_customer WHERE email = 'test_user@example.com';
    END IF;
    -- Insert customer
    IF NOT EXISTS (SELECT 1 FROM database_customer WHERE user_id = user_id) THEN
        INSERT INTO database_customer (user_id)
        VALUES (user_id)
        RETURNING id INTO customer_id;
    ELSE
        SELECT id INTO customer_id FROM database_customer WHERE user_id = user_id;
    END IF;

    -- Insert preferences
    INSERT INTO database_userpreference (user_id, budget_range, purchase_history)
    SELECT c.id,
       '{"min": 5000, "max": 50000}'::jsonb,
       '[]'::jsonb
    FROM database_customer c
    WHERE NOT EXISTS (SELECT 1 FROM database_userpreference up WHERE up.user_id = c.id);

    INSERT INTO database_userpreference_preferred_brands (userpreference_id, brand_id)
    SELECT up.id, b.id
    FROM database_userpreference up
    JOIN database_customer c ON up.user_id = c.id
    JOIN database_brand b ON b.name = 'Brand 1'
    WHERE NOT EXISTS (
        SELECT 1 FROM database_userpreference_preferred_brands 
        WHERE userpreference_id = up.id AND brand_id = b.id
    );

    INSERT INTO database_userpreference_preferred_categories (userpreference_id, category_id)
    SELECT up.id, ca.id
    FROM database_userpreference up
    JOIN database_customer cu ON up.user_id = cu.id
    JOIN database_category ca ON ca.name = 'Category 1'
    WHERE NOT EXISTS (
        SELECT 1 FROM database_userpreference_preferred_categories 
        WHERE userpreference_id = up.id AND category_id = ca.id
    );

END;
$$ LANGUAGE plpgsql;

    

