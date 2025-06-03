-- Crear la base de datos con soporte UTF-8
DROP DATABASE IF EXISTS final_db;
CREATE DATABASE final_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE final_db;

-- FOR KNOW THE STATUS OF THE TICKET: 1:Valid, 2:Expired, 3:Canceled
CREATE TABLE ticket_status (
    tic_status_id INT NOT NULL,
    description VARCHAR(20) NOT NULL,
    PRIMARY KEY (tic_status_id)
) ENGINE=InnoDB;

CREATE TABLE event (
    ev_id INT NOT NULL AUTO_INCREMENT,
    ev_name VARCHAR(100) NOT NULL,
    ev_description VARCHAR(200) NOT NULL,
    ev_date DATE NOT NULL UNIQUE,
    PRIMARY KEY (ev_id),
    INDEX idx_ev_date (ev_date)
) ENGINE=InnoDB;

CREATE TABLE venue (
    vn_id INT NOT NULL AUTO_INCREMENT,
    vn_name VARCHAR(100) NOT NULL,
    vn_type ENUM('VIP', 'General', 'Premium') NOT NULL,
    vn_capacity INT NOT NULL,
    PRIMARY KEY (vn_id),
    CONSTRAINT chk_capacity CHECK (vn_capacity > 0)
) ENGINE=InnoDB;

-- Relationship table "Event-Venue" one-to-many
CREATE TABLE event_venue (
    ev_ven_id INT NOT NULL AUTO_INCREMENT,
    ev_id INT NOT NULL,
    vn_id INT NOT NULL,
    PRIMARY KEY (ev_ven_id),
    FOREIGN KEY (ev_id) REFERENCES event(ev_id) ON DELETE CASCADE,
    FOREIGN KEY (vn_id) REFERENCES venue(vn_id) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE supplier (
    sup_id INT NOT NULL AUTO_INCREMENT,
    sup_company_name VARCHAR(100) NOT NULL,
    sup_contact_number VARCHAR(10) NOT NULL,
    sup_service_type VARCHAR(100) NOT NULL,
    PRIMARY KEY (sup_id),
    INDEX idx_service_type (sup_service_type),
    CONSTRAINT chk_contact_number CHECK (sup_contact_number REGEXP '^09[0-9]{8}$')
) ENGINE=InnoDB;


CREATE TABLE staff (
    stf_id INT NOT NULL AUTO_INCREMENT,
    stf_name VARCHAR(100) NOT NULL,
    stf_last_name VARCHAR(100) NOT NULL,
    stf_tasks VARCHAR(100) NOT NULL,
    stf_role VARCHAR(100) NOT NULL,
    sup_id INT NOT NULL,
    PRIMARY KEY (stf_id),
    FOREIGN KEY (sup_id) REFERENCES supplier(sup_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Relationship table "Staff-Venue" many-to-many
CREATE TABLE staff_venue (
    sv_id INT NOT NULL AUTO_INCREMENT,
    ev_id INT NOT NULL,
    stf_id INT NOT NULL,
    vn_id INT NOT NULL,
    PRIMARY KEY (sv_id),
    FOREIGN KEY (stf_id) REFERENCES staff(stf_id) ON DELETE CASCADE,
    FOREIGN KEY (vn_id) REFERENCES venue(vn_id) ON DELETE CASCADE,
    FOREIGN KEY (ev_id) REFERENCES event(ev_id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (ev_id, stf_id, vn_id)
) ENGINE=InnoDB;

CREATE TABLE attendee (
    att_id INT NOT NULL AUTO_INCREMENT,
    att_name VARCHAR(100) NOT NULL,
    att_last_name VARCHAR(100) NOT NULL,
    att_email VARCHAR(100) NOT NULL,
    att_phone VARCHAR(10) NOT NULL,
    PRIMARY KEY (att_id),
    UNIQUE INDEX idx_email (att_email),
    CONSTRAINT chk_correo_valido
        CHECK (att_email REGEXP '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_phone
        CHECK (att_phone REGEXP '^09[0-9]{8}$')
) ENGINE=InnoDB;

-- We can have 3 types of tickets: VIP, General, Premium
CREATE TABLE ticket (
    tic_id INT NOT NULL AUTO_INCREMENT,
    tic_type ENUM('VIP', 'General', 'Premium') NOT NULL,
    tic_status_id INT NOT NULL,
    ev_id INT NOT NULL,
    PRIMARY KEY (tic_id),
    FOREIGN KEY (tic_status_id) REFERENCES ticket_status(tic_status_id) ON UPDATE CASCADE,
    FOREIGN KEY (ev_id) REFERENCES event(ev_id) ON DELETE CASCADE,
    INDEX idx_ticket_status (tic_status_id)
) ENGINE=InnoDB;

-- types of purchase: Web:Online, APP:Mobile app, Physical ticket:Box Office
CREATE TABLE purchase (
    purchase_date DATE NOT NULL,
    purchase_type ENUM('Online', 'Mobile App', 'Box Office') NOT NULL,
    att_id INT NOT NULL,
    tic_id INT NOT NULL,
    PRIMARY KEY (att_id, tic_id),
    FOREIGN KEY (att_id) REFERENCES attendee(att_id) ON DELETE CASCADE,
    FOREIGN KEY (tic_id) REFERENCES ticket(tic_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============ UPLOAD DATA  ============ --

START TRANSACTION;

-- Ticket Status
INSERT INTO ticket_status (tic_status_id, description) VALUES 
(1, 'Valid'),
(2, 'Expired'),
(3, 'Canceled');

-- Suppliers
INSERT INTO supplier (sup_company_name, sup_contact_number, sup_service_type) VALUES
('Cleaning Professionals', '0987654321', 'Cleaning Services'),
('Elite Catering Co.', '0965432187', 'Catering Services'),
('Technodogs Productions', '0965588946', 'Sound Equipment'),
('Max Segurity Solutions', '0976543210', 'Security Services'),
('Lux Lighting', '0932145687', 'Lighting Systems'),
('S.L.A Media', '0998877665', 'Photography Services');

-- Events
INSERT INTO event (ev_name, ev_description, ev_date) VALUES
('Summer Cybersecurity Conference 2024', 
 'Annual technology conference featuring cybersecurity workshops and expert panels', 
 '2024-07-15'),
('Winter Gala 2024', 'New Year celebration with international artists', '2024-12-20'),
('TECHNODOGS Festival', '24h Outdoor Techno music festival with food trucks', '2024-04-10');

-- Venues
INSERT INTO venue (vn_name, vn_type, vn_capacity) VALUES
('Executive Boardroom', 'VIP', 10), -- Conference Venues
('Plenary Hall', 'Premium', 40),
('Networking Lounge', 'General', 50),
('Exhibition Center', 'General', 60),
('Champagne Reception', 'VIP', 12),-- Gala Venues
('Celebrity Lounge', 'VIP', 8),
('Gourmet Dining Room', 'Premium', 35),
('Skyline Terrace', 'Premium', 25),
('Garden Pavilion', 'General', 45),
('Artist Green Room', 'VIP', 20),-- Festival Venues
('VIP Deck', 'VIP', 15),
('Main Stage', 'Premium', 100),
('Dance Arena', 'Premium', 80),
('General Admission Field', 'General', 200),
('Food & Beverage Zone', 'General', 150);

-- Assign Venues to an event
INSERT INTO event_venue (ev_id, vn_id) VALUES
(1, 2),
(1, 3),
(1, 4),
(2, 7),
(2, 9),
(3, 12),
(3, 14),
(3, 15);


-- Cleaning Professionals (sup_id = 1)
INSERT INTO staff (stf_name, stf_last_name, stf_tasks, stf_role, sup_id) VALUES
('Robert', 'Garcia', 'Restroom maintenance', 'Cleaning Staff', 1),
('Maria', 'Lopez', 'Trash collection', 'Cleaning Assistant', 1),
('James', 'Wilson', 'Floor cleaning', 'Janitor', 1);

-- Elite Catering Co. (sup_id = 2)
INSERT INTO staff (stf_name, stf_last_name, stf_tasks, stf_role, sup_id) VALUES
('Anna', 'Martinez', 'Food preparation', 'Sous Chef', 2),
('Daniel', 'Taylor', 'Beverage service', 'Bartender', 2),
('Lisa', 'Anderson', 'Table setup', 'Wait Staff', 2),
('Thomas', 'White', 'Dishwashing', 'Kitchen Assistant', 2);

-- Technodogs Productions (sup_id = 3)
INSERT INTO staff (stf_name, stf_last_name, stf_tasks, stf_role, sup_id) VALUES
('Daniel', 'Troya', 'Speaker setup', 'Audio Technician', 3),
('Olivia', 'Martin', 'Microphone testing', 'Sound Assistant', 3),
('Kevin', 'Clark', 'Equipment transport', 'Stagehand', 3);

-- Max Security Solutions (sup_id = 4)
INSERT INTO staff (stf_name, stf_last_name, stf_tasks, stf_role, sup_id) VALUES
('Steven', 'Lewis', 'Entrance control', 'Security Guard', 4),
('Nancy', 'Walker', 'Crowd monitoring', 'Security Officer', 4),
('Richard', 'Hall', 'Emergency response', 'Security Staff', 4);

-- Lux Lighting (sup_id = 5)
INSERT INTO staff (stf_name, stf_last_name, stf_tasks, stf_role, sup_id) VALUES
('Patricia', 'Young', 'Light positioning', 'Lighting Technician', 5),
('Charles', 'Allen', 'Cable management', 'Electrician', 5),
('Jessica', 'King', 'Effect programming', 'Lighting Operator', 5);

-- S.L.A Media (sup_id = 6)
INSERT INTO staff (stf_name, stf_last_name, stf_tasks, stf_role, sup_id) VALUES
('Matthew', 'Scott', 'Photo editing', 'Assistant Photographer', 6),
('Ariel', 'Calle', 'Equipment setup', 'Photo Technician', 6),
('Mark', 'Adams', 'Guest photos', 'Event Photographer', 6);

-- Staff assignments 
-- Summer Cybersecurity Conference 2024 (ev_id 1)
INSERT INTO staff_venue (ev_id, stf_id, vn_id) VALUES
(1, 1, 3),
(1, 2, 4),
(1, 10, 2),
(1, 11, 3),
(1, 8, 2),
(1, 15, 2),
(1, 18, 4);

-- Winter Gala 2024 (ev_id 2)
INSERT INTO staff_venue (ev_id, stf_id, vn_id) VALUES
(2, 5, 7),
(2, 6, 9),
(2, 10, 7),
(2, 12, 9),
(2, 13, 7),
(2, 14, 9),
(2, 16, 7),
(2, 18, 9);

-- TECHNODOGS Festival (ev_id 3)
INSERT INTO staff_venue (ev_id, stf_id, vn_id) VALUES
(3, 8, 12),
(3, 9, 12),
(3, 11, 14),
(3, 12, 15),
(3, 13, 12),
(3, 15, 12),
(3, 17, 14),
(3, 18, 12);

-- Attendees (27), EV1=7, EV2=5, EV3=15
INSERT INTO attendee (att_id, att_name, att_last_name, att_email, att_phone) VALUES
(1, 'Liam', 'Smith', 'liam.smith1@example.com', '0933914947'),
(2, 'Emma', 'Johnson', 'emma.johnson2@example.com', '0957192539'),
(3, 'Noah', 'Williams', 'noah.williams3@example.com', '0959674572'),
(4, 'Olivia', 'Jones', 'olivia.jones4@example.com', '0958182551'),
(5, 'Elijah', 'Brown', 'elijah.brown5@example.com', '0954138031'),
(6, 'Ava', 'Davis', 'ava.davis6@example.com', '0913144407'),
(7, 'James', 'Miller', 'james.miller7@example.com', '0955534585'),
(8, 'Sophia', 'Wilson', 'sophia.wilson8@example.com', '0911720867'),
(9, 'Benjamin', 'Moore', 'benjamin.moore9@example.com', '0939646044'),
(10, 'Isabella', 'Taylor', 'isabella.taylor10@example.com', '0957293694'),
(11, 'Lucas', 'Anderson', 'lucas.anderson11@example.com', '0930522870'),
(12, 'Mia', 'Thomas', 'mia.thomas12@example.com', '0942001867'),
(13, 'Mason', 'Jackson', 'mason.jackson13@example.com', '0932672836'),
(14, 'Charlotte', 'White', 'charlotte.white14@example.com', '0992191087'),
(15, 'Ethan', 'Harris', 'ethan.harris15@example.com', '0921330634'),
(16, 'Amelia', 'Martin', 'amelia.martin16@example.com', '0953684092'),
(17, 'Alexander', 'Thompson', 'alexander.thompson17@example.com', '0926200029'),
(18, 'Harper', 'Garcia', 'harper.garcia18@example.com', '0966082965'),
(19, 'Henry', 'Martinez', 'henry.martinez19@example.com', '0951836443'),
(20, 'Evelyn', 'Robinson', 'evelyn.robinson20@example.com', '0919473687'),
(21, 'Sebastian', 'Clark', 'sebastian.clark21@example.com', '0957564872'),
(22, 'Abigail', 'Rodriguez', 'abigail.rodriguez22@example.com', '0917151805'),
(23, 'Jack', 'Lewis', 'jack.lewis23@example.com', '0922308531'),
(24, 'Emily', 'Lee', 'emily.lee24@example.com', '0913063760'),
(25, 'Owen', 'Walker', 'owen.walker25@example.com', '0934568023'),
(26, 'Elizabeth', 'Hall', 'elizabeth.hall26@example.com', '0914143953'),
(27, 'Daniel', 'Allen', 'daniel.allen27@example.com', '0933525410');



-- Tickets (27)
INSERT INTO ticket (tic_id, tic_type, tic_status_id, ev_id) VALUES
(1, 'Premium', 1, 1),
(2, 'General', 1, 1),
(3, 'General', 1, 1),
(4, 'VIP', 1, 1),
(5, 'General', 1, 1),
(6, 'VIP', 1, 1),
(7, 'General', 1, 1),
(8, 'VIP', 1, 2),
(9, 'Premium', 1, 2),
(10, 'VIP', 1, 2),
(11, 'Premium', 1, 2),
(12, 'Premium', 1, 2),
(13, 'General', 1, 3),
(14, 'VIP', 1, 3),
(15, 'Premium', 1, 3),
(16, 'VIP', 1, 3),
(17, 'VIP', 1, 3),
(18, 'Premium', 1, 3),
(19, 'General', 1, 3),
(20, 'General', 1, 3),
(21, 'Premium', 1, 3),
(22, 'Premium', 1, 3),
(23, 'General', 1, 3),
(24, 'General', 1, 3),
(25, 'VIP', 1, 3),
(26, 'Premium', 1, 3),
(27, 'VIP', 1, 3);


-- Compras
INSERT INTO purchase (purchase_date, purchase_type, att_id, tic_id) VALUES
('2024-06-04', 'Mobile App', 1, 1),
('2024-06-08', 'Online', 2, 2),
('2024-06-09', 'Mobile App', 3, 3),
('2024-07-01', 'Box Office', 4, 4),
('2024-06-22', 'Mobile App', 5, 5),
('2024-06-16', 'Online', 6, 6),
('2024-06-23', 'Online', 7, 7),
('2024-06-14', 'Box Office', 8, 8),
('2024-06-08', 'Mobile App', 9, 9),
('2024-06-22', 'Box Office', 10, 10),
('2024-06-03', 'Online', 11, 11),
('2024-06-15', 'Mobile App', 12, 12),
('2024-06-11', 'Online', 13, 13),
('2024-06-28', 'Online', 14, 14),
('2024-06-08', 'Online', 15, 15),
('2024-06-01', 'Online', 16, 16),
('2024-06-18', 'Box Office', 17, 17),
('2024-06-13', 'Online', 18, 18),
('2024-06-11', 'Mobile App', 19, 19),
('2024-06-07', 'Mobile App', 20, 20),
('2024-07-01', 'Mobile App', 21, 21),
('2024-06-06', 'Online', 22, 22),
('2024-06-28', 'Online', 23, 23),
('2024-06-25', 'Box Office', 24, 24),
('2024-06-15', 'Online', 25, 25),
('2024-06-30', 'Online', 26, 26),
('2024-06-01', 'Mobile App', 27, 27);

COMMIT;

