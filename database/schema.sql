-- Raw SQL schema for reference

-- =============================================
-- Version 2: Transport Management & Dispatch Engine
-- =============================================

CREATE TABLE trips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_number VARCHAR(20) NOT NULL UNIQUE,
    vehicle_id INT NOT NULL,
    driver_id INT NULL,
    source VARCHAR(200) NOT NULL,
    destination VARCHAR(200) NOT NULL,
    cargo_weight FLOAT NOT NULL,
    planned_distance FLOAT NOT NULL,
    actual_distance FLOAT NULL,
    estimated_duration VARCHAR(50) NULL,
    dispatch_time DATETIME NULL,
    completion_time DATETIME NULL,
    fuel_consumed FLOAT NULL,
    final_odometer INT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Draft',
    remarks TEXT NULL,
    created_by INT NOT NULL,
    updated_by INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id),
    INDEX idx_trip_number (trip_number),
    INDEX idx_trip_status (status)
);

CREATE TABLE trip_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    previous_status VARCHAR(20) NULL,
    new_status VARCHAR(20) NOT NULL,
    changed_by INT NOT NULL,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(id),
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

CREATE TABLE activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    details TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- =============================================
-- Version 3: Smart Operations
-- =============================================

CREATE TABLE maintenance_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    maintenance_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    workshop_name VARCHAR(100) NOT NULL,
    estimated_cost FLOAT NOT NULL,
    actual_cost FLOAT NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Scheduled',
    remarks TEXT NULL,
    created_by INT NOT NULL,
    updated_by INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

CREATE TABLE fuel_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NULL,
    vehicle_id INT NOT NULL,
    driver_id INT NULL,
    fuel_station VARCHAR(100) NULL,
    liters FLOAT NOT NULL,
    cost_per_liter FLOAT NOT NULL,
    total_cost FLOAT NOT NULL,
    odometer INT NOT NULL,
    fuel_date DATE NOT NULL,
    receipt_number VARCHAR(50) NULL,
    remarks TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id)
);

CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NULL,
    vehicle_id INT NULL,
    expense_type VARCHAR(50) NOT NULL,
    amount FLOAT NOT NULL,
    description TEXT NOT NULL,
    expense_date DATE NOT NULL,
    receipt_reference VARCHAR(50) NULL,
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

