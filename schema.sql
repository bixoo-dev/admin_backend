CREATE TABLE admins (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    phone VARCHAR(50),
    department VARCHAR(100),
    role_title VARCHAR(100),
    employee_id VARCHAR(50),
    status VARCHAR(50) DEFAULT 'ACTIVE',
    joined_date DATE,
    last_active VARCHAR(100),
    login_ip VARCHAR(50),
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    onboarding_step VARCHAR(255),
    invite_link VARCHAR(255),
    invite_sent_at TIMESTAMP NULL,
    modules JSON,
    activity_summary JSON,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    id VARCHAR(50) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    contact_masked VARCHAR(50),
    gstin VARCHAR(50),
    verification_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE catalog_listings (
    id VARCHAR(50) PRIMARY KEY,
    seller_id VARCHAR(50) NOT NULL,
    category VARCHAR(255),
    product_name VARCHAR(255),
    unit_price VARCHAR(50),
    status VARCHAR(50),
    is_flagged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES accounts(id)
);

CREATE TABLE requirements (
    id VARCHAR(50) PRIMARY KEY,
    buyer_id VARCHAR(50) NOT NULL,
    product VARCHAR(255),
    total_requested DECIMAL(15,2),
    unit VARCHAR(20),
    remaining_qty DECIMAL(15,2),
    deadline DATE,
    status VARCHAR(50),
    is_flagged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES accounts(id)
);

CREATE TABLE orders (
    id VARCHAR(50) PRIMARY KEY,
    buyer_id VARCHAR(50) NOT NULL,
    seller_id VARCHAR(50) NOT NULL,
    source_type VARCHAR(50),
    source_ref VARCHAR(50),
    agreed_qty VARCHAR(100),
    total_value VARCHAR(100),
    logistics_linked VARCHAR(50),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES accounts(id),
    FOREIGN KEY (seller_id) REFERENCES accounts(id)
);

CREATE TABLE offers (
    id VARCHAR(50) PRIMARY KEY,
    requirement_id VARCHAR(50) NOT NULL,
    buyer_id VARCHAR(50) NOT NULL,
    seller_id VARCHAR(50) NOT NULL,
    offered_qty VARCHAR(100),
    latest_price VARCHAR(100),
    status VARCHAR(50),
    history_count INT DEFAULT 0,
    linked_order_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id),
    FOREIGN KEY (buyer_id) REFERENCES accounts(id),
    FOREIGN KEY (seller_id) REFERENCES accounts(id),
    FOREIGN KEY (linked_order_id) REFERENCES orders(id)
);

CREATE TABLE auctions (
    id VARCHAR(50) PRIMARY KEY,
    seller_id VARCHAR(50) NOT NULL,
    product VARCHAR(255),
    status VARCHAR(50),
    winner_computed BOOLEAN DEFAULT FALSE,
    winning_buyer_id VARCHAR(50),
    winning_amount VARCHAR(100),
    winning_timestamp TIMESTAMP NULL,
    linked_order_id VARCHAR(50),
    is_flagged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES accounts(id),
    FOREIGN KEY (winning_buyer_id) REFERENCES accounts(id),
    FOREIGN KEY (linked_order_id) REFERENCES orders(id)
);

CREATE TABLE trips (
    id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    transporter VARCHAR(255),
    route VARCHAR(255),
    current_milestone VARCHAR(50),
    gps_last_seen VARCHAR(100),
    is_gps_stale BOOLEAN DEFAULT FALSE,
    consignee_proof_submitted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE settlements (
    id VARCHAR(50) PRIMARY KEY,
    trip_id VARCHAR(50) NOT NULL,
    payee VARCHAR(255),
    amount VARCHAR(100),
    proof_status VARCHAR(50),
    settlement_status VARCHAR(50),
    bank_ref_masked VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);

CREATE TABLE cases (
    id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50),
    linked_entity VARCHAR(50),
    reporter_id VARCHAR(50) NOT NULL,
    status VARCHAR(50),
    sla VARCHAR(50),
    evidence_attached BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_id) REFERENCES accounts(id)
);

CREATE TABLE reports (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    last_run TIMESTAMP NULL,
    format VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actor_id VARCHAR(50) NOT NULL,
    action VARCHAR(100),
    target_id VARCHAR(50),
    reason TEXT,
    ip_address VARCHAR(50),
    case_ref VARCHAR(50),
    FOREIGN KEY (actor_id) REFERENCES admins(id)
);