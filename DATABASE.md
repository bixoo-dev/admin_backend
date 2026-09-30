# BIXOO Database Documentation

## Tables

### `admins`
- **Purpose**: Stores Admin and Super Admin users.
- **Key Fields**: `id` (PK), `email` (Unique), `password_hash`, `role` (ADMIN, SUPER_ADMIN).

### `accounts`
- **Purpose**: Business entities (Buyers, Sellers, Transporters).
- **Key Fields**: `id` (PK), `entity_type`, `verification_status`.

### `catalog_listings`
- **Purpose**: Seller product catalog items.
- **Key Fields**: `id` (PK), `seller_id` (FK -> accounts.id).

### `requirements`
- **Purpose**: Buyer demands/requirements.
- **Key Fields**: `id` (PK), `buyer_id` (FK -> accounts.id).

### `orders`
- **Purpose**: Finalized trades/orders.
- **Key Fields**: `id` (PK), `buyer_id`, `seller_id` (FK -> accounts.id).

### `offers`
- **Purpose**: Bids/Offers against requirements.
- **Key Fields**: `id` (PK), `requirement_id` (FK), `linked_order_id` (FK).

### `auctions`
- **Purpose**: Live seller auctions.
- **Key Fields**: `id` (PK), `seller_id` (FK), `winning_buyer_id` (FK), `linked_order_id` (FK).

### `trips`
- **Purpose**: Logistics tracking for orders.
- **Key Fields**: `id` (PK), `order_id` (FK -> orders.id).

### `settlements`
- **Purpose**: Financial settlement ledger for trips.
- **Key Fields**: `id` (PK), `trip_id` (FK -> trips.id).

### `cases`
- **Purpose**: Dispute resolution cases.
- **Key Fields**: `id` (PK), `reporter_id` (FK -> accounts.id).

### `audit_logs`
- **Purpose**: Admin intervention tracking.
- **Key Fields**: `id` (PK), `actor_id` (FK -> admins.id).

## Relationships
- `admins` -> `audit_logs` (1:N)
- `accounts` -> `requirements` / `catalog_listings` / `auctions` / `offers` / `orders` (1:N)
- `orders` -> `trips` (1:N)
- `trips` -> `settlements` (1:N)
