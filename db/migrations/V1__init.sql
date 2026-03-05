
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS plane_status (
    id SERIAL PRIMARY KEY,
    state VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS payment_types (
    id SERIAL PRIMARY KEY,
    type VARCHAR(255) NOT NULL UNIQUE,
    details TEXT
);

CREATE TABLE IF NOT EXISTS itinerary_types (
    id SERIAL PRIMARY KEY,
    type VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS airport_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    created_at DATE NOT NULL,
    disabled_at DATE,
    address VARCHAR(255),
    status BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS balances (
    id SERIAL PRIMARY KEY,
    balance NUMERIC(10, 2) NOT NULL,
    user_id INT NOT NULL,
    CONSTRAINT fk_balances_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(10, 2) NOT NULL,
    issued_date DATE NOT NULL,
    description TEXT,
    payment_type_id INT,
    balance_id INT,
    CONSTRAINT fk_transactions_payment_type_id FOREIGN KEY (payment_type_id) REFERENCES payment_types(id),
    CONSTRAINT fk_transactions_balance_id FOREIGN KEY (balance_id) REFERENCES balances(id)
);

CREATE TABLE IF NOT EXISTS planes (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    registration VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(255) NOT NULL,
    acquisition_date DATE NOT NULL,
    consumption_per_hour INT NOT NULL,
    fare NUMERIC(10, 2) NOT NULL,
    description TEXT,
    plane_status_id INT,
    CONSTRAINT fk_planes_plane_status_id FOREIGN KEY (plane_status_id) REFERENCES plane_status(id)
);

CREATE TABLE IF NOT EXISTS flight_sessions (
    id SERIAL PRIMARY KEY,
    flight_session_identifier INT NOT NULL,
    issued_date DATE NOT NULL,
    observations TEXT,
    transaction_id INT,
    CONSTRAINT fk_flight_sessions_transaction_id FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

CREATE TABLE IF NOT EXISTS itineraries (
    id SERIAL PRIMARY KEY,
    departure_time TIMESTAMP NOT NULL,
    arrival_time TIMESTAMP NOT NULL,
    landings_amount INT NOT NULL,
    observations TEXT,
    itinerary_type_id INT,
    plane_id INT,
    invoice_id INT,
    CONSTRAINT fk_itineraries_itinerary_type_id FOREIGN KEY (itinerary_type_id) REFERENCES itinerary_types(id),
    CONSTRAINT fk_itineraries_plane_id FOREIGN KEY (plane_id) REFERENCES planes(id),
    CONSTRAINT fk_itineraries_invoice_id FOREIGN KEY (invoice_id) REFERENCES flight_sessions(id)
);

CREATE TABLE IF NOT EXISTS users_have_roles (
    users_id INT,
    roles_id INT,
    PRIMARY KEY (users_id, roles_id),
    CONSTRAINT fk_uhr_users_id FOREIGN KEY (users_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_uhr_roles_id FOREIGN KEY (roles_id) REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users_have_flight_sessions (
    users_id INT,
    flight_sessions INT,
    PRIMARY KEY (users_id, flight_sessions),
    CONSTRAINT fk_uhf_users_id FOREIGN KEY (users_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_uhf_flight_sessions FOREIGN KEY (flight_sessions) REFERENCES flight_sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS itinerary_has_airport_codes (
    itinerary_id INT,
    aeroport_codes_id INT,
    PRIMARY KEY (itinerary_id, aeroport_codes_id),
    CONSTRAINT fk_ihac_itinerary_id FOREIGN KEY (itinerary_id) REFERENCES itineraries(id) ON DELETE CASCADE,
    CONSTRAINT fk_ihac_airport_codes_id FOREIGN KEY (aeroport_codes_id) REFERENCES airport_codes(id) ON DELETE CASCADE
);
