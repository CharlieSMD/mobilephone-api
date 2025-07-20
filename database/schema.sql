-- Mobile Phone Catalogue Database Schema
-- Week 2: Database Design

-- Drop tables if they exist (for development)
DROP TABLE IF EXISTS ratings CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS favorites CASCADE;
DROP TABLE IF EXISTS phone_specs CASCADE;
DROP TABLE IF EXISTS phones CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Phones table
CREATE TABLE phones (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    release_year INTEGER,
    price DECIMAL(10,2),
    image_url VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(brand, model)
);

-- PhoneSpecs table (1:1 relationship with Phones)
CREATE TABLE phone_specs (
    id SERIAL PRIMARY KEY,
    phone_id INTEGER UNIQUE REFERENCES phones(id) ON DELETE CASCADE,
    screen_size DECIMAL(4,2), -- inches
    resolution VARCHAR(20),
    processor VARCHAR(100),
    ram VARCHAR(20),
    storage VARCHAR(50),
    battery_capacity INTEGER, -- mAh
    camera_main VARCHAR(50),
    camera_front VARCHAR(50),
    os VARCHAR(50),
    weight DECIMAL(5,2), -- grams
    dimensions VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Favorites table (Many-to-Many relationship between Users and Phones)
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    phone_id INTEGER REFERENCES phones(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, phone_id)
);

-- Comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    phone_id INTEGER REFERENCES phones(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ratings table
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    phone_id INTEGER REFERENCES phones(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, phone_id)
);

-- Create indexes for better performance
CREATE INDEX idx_phones_brand ON phones(brand);
CREATE INDEX idx_phones_model ON phones(model);
CREATE INDEX idx_comments_phone_id ON comments(phone_id);
CREATE INDEX idx_ratings_phone_id ON ratings(phone_id);
CREATE INDEX idx_favorites_user_id ON favorites(user_id);
CREATE INDEX idx_favorites_phone_id ON favorites(phone_id);

-- Insert sample data for testing
INSERT INTO users (username, email, password_hash, first_name, last_name) VALUES
('john_doe', 'john@example.com', 'hashed_password_1', 'John', 'Doe'),
('jane_smith', 'jane@example.com', 'hashed_password_2', 'Jane', 'Smith');

INSERT INTO phones (brand, model, release_year, price, description) VALUES
('Apple', 'iPhone 15 Pro', 2023, 999.99, 'Latest iPhone with advanced camera system'),
('Samsung', 'Galaxy S24 Ultra', 2024, 1199.99, 'Premium Android flagship with S Pen'),
('Google', 'Pixel 8 Pro', 2023, 899.99, 'Google''s flagship with advanced AI features');

INSERT INTO phone_specs (phone_id, screen_size, resolution, processor, ram, storage, battery_capacity, camera_main, camera_front, os, weight, dimensions) VALUES
(1, 6.1, '2556x1179', 'A17 Pro', '8GB', '128GB', 3274, '48MP + 12MP + 12MP', '12MP', 'iOS 17', 187, '146.7 x 71.5 x 8.25mm'),
(2, 6.8, '3088x1440', 'Snapdragon 8 Gen 3', '12GB', '256GB', 5000, '200MP + 12MP + 50MP + 10MP', '12MP', 'Android 14', 232, '163.4 x 79.0 x 8.6mm'),
(3, 6.7, '2992x1344', 'Google Tensor G3', '12GB', '128GB', 4950, '50MP + 48MP + 48MP', '10.5MP', 'Android 14', 213, '162.6 x 76.5 x 8.8mm'); 