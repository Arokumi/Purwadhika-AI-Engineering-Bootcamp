CREATE DATABASE IF NOT EXISTS car_rentals;
USE car_rentals;

-- Dropping Tables --
DROP TABLE IF EXISTS rentals;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS cars;

-- Creating Tables --
CREATE TABLE users (
	user_id int NOT NULL AUTO_INCREMENT,
    user_name varchar(100) NOT NULL,
    user_password varchar(100) NOT NULL,
    PRIMARY KEY (user_id),
    UNIQUE (user_name)
);

CREATE TABLE employees (
	employee_id int NOT NULL AUTO_INCREMENT,
    employee_name varchar(100) NOT NULL,
    employee_password varchar(100) NOT NULL,
    employee_commission decimal(4, 3) NOT NULL,
    PRIMARY KEY (employee_id),
    UNIQUE (employee_name)
);

CREATE TABLE cars (
    car_id int NOT NULL AUTO_INCREMENT,
	car_plate varchar(11),
    car_make varchar(20) NOT NULL,
    car_model varchar(20) NOT NULL,
    car_category varchar(20) NOT NULL,
    car_year year NOT NULL,
    car_km int NOT NULL,
    car_fee int NOT NULL,
    PRIMARY KEY (car_id),
    UNIQUE (car_plate)
);

CREATE TABLE rentals (
	rental_id int NOT NULL AUTO_INCREMENT,
    renter_id int NOT NULL,
    rentee_id int NOT NULL,
    vehicle_id int NOT NULL,
    rental_start date NOT NULL,
    rental_end date NOT NULL,
    PRIMARY KEY (rental_id),
    FOREIGN KEY (renter_id) REFERENCES employees (employee_id),
    FOREIGN KEY (rentee_id) REFERENCES users (user_id),
    FOREIGN KEY (vehicle_id) REFERENCES cars (car_id)
);

-- Inserting Values --
INSERT INTO users(user_name, user_password) values 
('John', '04d35637718123aa6d31aa52354fc7efdc564366072e4d12ed1cc7bd80db52d9'), -- Password = Aura12!@
('Renggo', '2fb74c3353e373e877b7cfb4f0388136f7dfcfd2e3792ba969a34f7e3f120d69'), -- Password = ImGonnaDo1t!
('Darrel', '8c388bb34827bc3997b11f848f86397780f5f36e626b7adc4b84fe38bc35af0e'), -- Password = Hurhur+H4h4
('Dharma', 'b78a1f94dfaa3b6706907cd481c741347e40459bbc8fd3c617b97f9436e182b2'), -- Password = MaiMaiMastr12#$
('Ryu', 'b85655ce51f36bbfeb101b0e8921fd3ca385d8a823b271daa2bb0824a71dc0ac'), -- Password = Nitzche_202
('Andreas', 'd3b777eeb3317d073b3ba52f86641257596825ad3659c068cbbfac9b2b97005b'), -- Password = MisterD1Y?
('Giselle', '311a851f10ee126f2891434e8e2a72c9621dcb04c04d4d34688b8b67a8a62da3'), -- Password = Match4<3
('Mila', 'd4f4fb66efe72249a977cf162f851dc6c75388a2375ff7d2b4f797162d07fb42'), -- Password = @DrMcStu55ins
('Syifa', '63141a60b3d8790ae5899d9093cfe4f1cc3d824e5f2e8a4b36316ccc42db8d63'), -- Password = Wise$t10
('Sienna', '53b557b13a6f4c4bedabcb16dd34177de17572f5a376b577ae12e47eda849bfc'), -- Password = GoodReads50%
('Tyrone', '431199065410b633ef0ced19491700cfb7bc2a36228c8fc359262bf3265fd6c6'); -- Password = DragonWarriah#1

INSERT INTO employees(employee_name, employee_password, employee_commission) values 
('Lance', '415191fb534eeb526f9a617b0e85c10858a898ef29c26e751b42d5377c137576', '0.07'), -- Password = Mithoco(5)
('Arvi', 'ccfb40e4edddcbfcfbb56c1bd0a6720b343f9b8a0743ce1836ce1ff85ec2daba', '0.06'), -- Password = R=V(12)
('Nick', 'fee5594dee7135e53a68e6a8a233ca6f1c5b410204b87a1f11b8fdf943eff98d', '0.05'); -- Password = C8H11No2


/*
Car Category Fee Guidelines
- Budget  : ~Rp 400,000 – Rp 600,000
- Family  : ~Rp 650,000 – Rp 1,000,000
- Luxury  : ~Rp 1,200,000 – Rp 2,000,000
*/

INSERT INTO cars(car_plate, car_make, car_model, car_category,car_year, car_km, car_fee) values
('B 1234 KQJ', 'Toyota', 'Corolla', 'Budget', '2019', '45000', '500000'), 
('D 5678 LMR', 'Honda', 'Brio', 'Budget', '2020', '25000', '450000'), 
('B 2468 NPT', 'Suzuki', 'Swift', 'Budget', '2018', '55000', '400000'), 
('D 1357 QRS', 'Nissan', 'March', 'Budget', '2021', '22000', '550000'), 
('B 9087 TUV', 'Chevrolet', 'Aveo', 'Budget', '2017', '70000', '420000'), 
('D 8045 WXY', 'Toyota', 'Innova', 'Family', '2020', '30000', '750000'), 
('B 6677 ZAB', 'Mitsubishi', 'Xpander', 'Family', '2021', '18000', '700000'), 
('D 5589 CDE', 'Honda', 'CR-V', 'Family', '2022', '12000', '950000'), 
('B 4456 FGH', 'Toyota', 'Fortuner', 'Family', '2021', '28000', '1000000'), 
('D 7890 JKL', 'Kia', 'Sportage', 'Family', '2019', '40000', '800000'), 
('B 1122 MNO', 'BMW', '3 Series', 'Luxury', '2021', '15000', '1500000'), 
('D 3344 PQR', 'Mercedes', 'C-Class', 'Luxury', '2022', '10000', '1800000'), 
('B 5566 STU', 'Tesla', 'Model 3', 'Luxury', '2022', '8000', '2000000'), 
('D 7788 VWX', 'Lexus', 'RX 350', 'Luxury', '2020', '25000', '1700000'), 
('B 9900 YZA', 'Jeep', 'Wrangler', 'Luxury', '2019', '35000', '1600000');

INSERT INTO rentals(renter_id, rentee_id, vehicle_id, rental_start, rental_end) values
('1', '3', '11', '2025-01-05', '2025-01-08'), 
('2', '7', '2', '2025-01-10', '2025-01-12'), 
('1', '5', '13', '2025-01-15', '2025-01-20'), 
('3', '1', '6', '2025-01-18', '2025-01-22'), 
('2', '9', '15', '2025-02-01', '2025-02-05'), 
('1', '10', '8', '2025-02-07', '2025-02-10'), 
('3', '2', '12', '2025-02-15', '2025-02-20'), 
('2', '6', '1', '2025-02-18', '2025-02-21'), 
('3', '8', '14', '2025-02-25', '2025-03-02'), 
('1', '4', '3', '2025-03-01', '2025-03-04'),
('2', '6', '11', '2025-01-09', '2025-01-12'),
('3', '9', '11', '2025-01-14', '2025-01-17'),
('1', '2', '12', '2025-02-20', '2025-02-23'),
('2', '4', '12', '2025-02-25', '2025-02-28'),
('1', '7', '13', '2025-01-20', '2025-01-23'),
('3', '1', '13', '2025-01-25', '2025-01-28'),
('1', '5', '14', '2025-03-02', '2025-03-04'),
('2', '3', '14', '2025-03-06', '2025-03-09'),
('1', '6', '2',  '2025-01-12', '2025-01-14'),
('2', '2', '2',  '2025-02-02', '2025-02-04'),
('1', '8', '6',  '2025-01-22', '2025-01-24'),
('2', '11', '6', '2025-01-26', '2025-01-29'),
('1', '1', '8',  '2025-02-10', '2025-02-12'),
('2', '9', '8',  '2025-02-14', '2025-02-16'),
('1', '11', '15', '2025-02-05', '2025-02-07'),
('2', '6', '15',  '2025-02-09', '2025-02-13'),
('1', '4', '1',   '2025-02-21', '2025-02-23'),
('2', '5', '1',   '2025-02-25', '2025-02-27'),
('3', '7', '3',   '2025-03-04', '2025-03-06'),
('1', '10', '4',  '2025-01-10', '2025-01-11'),
('2', '1', '5',   '2025-02-12', '2025-02-13'),
('3', '6', '7',   '2025-03-12', '2025-03-14'),
('1', '3', '9',   '2025-01-25', '2025-01-27'),
('2', '8', '10',  '2025-03-05', '2025-03-08');














