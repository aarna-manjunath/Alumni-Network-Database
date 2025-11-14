-- ========================================
-- Create and select database
-- ========================================
CREATE DATABASE AlumniDB;
USE AlumniDB;

-- Drop tables in correct dependency order
DROP TABLE IF EXISTS EventParticipation;
DROP TABLE IF EXISTS Event;
DROP TABLE IF EXISTS Committee;
DROP TABLE IF EXISTS Mentorship;
DROP TABLE IF EXISTS Education;
DROP TABLE IF EXISTS Alumni;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Department;

-- Department Table

CREATE TABLE Department (
    dept_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    hod VARCHAR(100) NOT NULL
);
INSERT INTO Department VALUES
(1, 'Computer Science', 'Dr. Meena Rao'),
(2, 'Electronics', 'Dr. Sanjay Patil'),
(3, 'Mechanical', 'Dr. Rajesh Sharma'),
(4, 'Civil', 'Dr. Kavita Nair'),
(5, 'Mathematics', 'Dr. Arun Desai');

-- Alumni Table

CREATE TABLE Alumni (
    alumni_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(10) UNIQUE,
    graduation_year INT NOT NULL CHECK (graduation_year >= 1990),
    company VARCHAR(100) DEFAULT 'Not Provided',
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);
INSERT INTO Alumni VALUES
(101, 'Ravi Kumar', 'ravi.k@alumni.edu', '9876543210', 2010, 'Infosys', 1),
(102, 'Sneha Patel', 'sneha.p@alumni.edu', '9988776655', 2012, 'TCS', 2),
(103, 'Arjun Mehta', 'arjun.m@alumni.edu', '9123456780', 2015, 'Bosch', 3),
(104, 'Meena Iyer', 'meena.i@alumni.edu', '9012345678', 2013, 'L&T', 4),
(105, 'Vikram Desai', 'vikram.d@alumni.edu', '8899776655', 2011, 'Google', 5);


-- Student Table

CREATE TABLE Student (
    student_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE,
    batch_year INT NOT NULL CHECK (batch_year >= 2000),
    dept_id INT DEFAULT 1,
    FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);
INSERT INTO Student VALUES
(201, 'Amit Sharma', 'amit.s@univ.edu', '9876501234', 2022, 1),
(202, 'Priya Nair', 'priya.n@univ.edu', '9876505678', 2021, 2),
(203, 'Rohit Verma', 'rohit.v@univ.edu', '9876509999', 2020, 3),
(204, 'Kavya Iyer', 'kavya.i@univ.edu', '9876512345', 2023, 1),
(205, 'Aditya Rao', 'aditya.r@univ.edu', '9876516789', 2022, 5);

-- Education Table

CREATE TABLE Education (
    edu_id INT,
    alumni_id INT,
    college_name VARCHAR(100) NOT NULL,
    degree VARCHAR(100) NOT NULL,
    course VARCHAR(100) NOT NULL,
    start_year INT NOT NULL,
    end_year INT NOT NULL,
    PRIMARY KEY (edu_id, alumni_id),
    FOREIGN KEY (alumni_id) REFERENCES Alumni(alumni_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

INSERT INTO Education (edu_id, alumni_id, college_name, degree, course, start_year, end_year) VALUES
(1, 101, 'PES University', 'B.Tech', 'Computer Science Engineering', 2006, 2010),
(2, 101, 'IISc Bangalore', 'M.Tech', 'Computer Science Engineering', 2011, 2013),

(1, 102, 'IIT Bombay', 'B.Tech', 'Electronics and Communication Engineering', 2008, 2012),
(2, 102, 'Stanford University', 'M.S', 'Electronics Engineering', 2013, 2015),

(1, 103, 'IISc Bangalore', 'M.Tech', 'Computer Science Engineering', 2013, 2015),
(2, 103, 'IIM Ahmedabad', 'MBA', 'Commerce', 2016, 2018),

(1, 104, 'NIT Trichy', 'B.Tech', 'Civil Engineering', 2009, 2013),

(1, 105, 'Delhi University', 'B.Sc', 'Mathematics', 2014, 2017),
(2, 105, 'Cambridge University', 'M.Sc', 'Applied Mathematics', 2018, 2020),
(3, 105, 'Cambridge University', 'PhD', 'Applied Mathematics', 2021, 2025);

-- Mentorship Table

CREATE TABLE Mentorship (
    mid INT PRIMARY KEY,
    alumni_id INT NOT NULL,
    student_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    FOREIGN KEY (alumni_id) REFERENCES Alumni(alumni_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE (alumni_id, student_id)
);
INSERT INTO Mentorship VALUES
(401, 101, 201, '2022-06-01', '2023-06-01'),
(402, 102, 202, '2021-07-01', '2022-07-01'),
(403, 103, 203, '2020-05-01', '2021-05-01'),
(404, 104, 204, '2023-01-01', '2023-12-31'),
(405, 105, 205, '2022-08-01', '2023-08-01');

-- Committee Table

CREATE TABLE Committee (
    cid INT,
    event_id INT,
    name VARCHAR(100),
    phone VARCHAR(15),
    head VARCHAR(100),
    PRIMARY KEY (cid, event_id),
    FOREIGN KEY (event_id) REFERENCES Event(event_id)
        ON DELETE CASCADE
);

INSERT INTO Committee (cid, event_id, name, phone, head) VALUES
(501, 601, 'TechFest Committee', '9001112233', 'Prof. Arjun'),     -- Linked to Tech Symposium
(502, 602, 'Cultural Committee', '9002223344', 'Prof. Sneha'),     -- Linked to Cultural Fest
(503, 603, 'Sports Committee', '9003334455', 'Prof. Rajesh'),      -- Linked to Sports Meet
(504, 604, 'Placement Committee', '9004445566', 'Prof. Kavita'),   -- Linked to Career Fair
(505, 605, 'Math Club', '9005556677', 'Prof. Arun');               -- Linked to Math Workshop


-- Event Table

CREATE TABLE Event (
    event_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    location VARCHAR(100) NOT NULL,
    date DATE NOT NULL
);
INSERT INTO Event VALUES
(601, 'Tech Symposium', 'Annual CS Symposium', 'Auditorium', '2023-08-20'),
(602, 'Cultural Fest', 'Music and Dance Festival', 'Open Ground', '2023-09-15'),
(603, 'Sports Meet', 'Inter-college Sports', 'Stadium', '2023-10-10'),
(604, 'Career Fair', 'Company Recruitment Drive', 'Convention Center', '2023-11-05'),
(605, 'Math Workshop', 'Applied Mathematics Workshop', 'Lab 101', '2023-12-01');

-- EventParticipation Table

-- Student participation
CREATE TABLE EventParticipationStudent (
    pid INT PRIMARY KEY,
    event_id INT NOT NULL,
    student_id INT NOT NULL,
    resp_status ENUM('Registered','Attended','Cancelled') DEFAULT 'Registered',
    FOREIGN KEY (event_id) REFERENCES Event(event_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Alumni participation
CREATE TABLE EventParticipationAlumni (
    pid INT PRIMARY KEY,
    event_id INT NOT NULL,
    alumni_id INT NOT NULL,
    resp_status ENUM('Registered','Attended','Cancelled') DEFAULT 'Registered',
    FOREIGN KEY (event_id) REFERENCES Event(event_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (alumni_id) REFERENCES Alumni(alumni_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
INSERT INTO EventParticipationStudent VALUES
(701, 601, 201, 'Attended'),     -- Aarav attended Tech Talk on AI
(702, 602, 202, 'Registered'),   -- Meera registered Robotics Workshop
(703, 603, 203, 'Cancelled'),    -- Rohan cancelled Cultural Fest
(704, 604, 204, 'Attended'),     -- Priya attended Football Match
(705, 605, 205, 'Registered');   -- Kabir registered Data Science Seminar

INSERT INTO EventParticipationAlumni VALUES
(801, 601, 101, 'Attended'),     -- Neha attended Tech Talk on AI
(802, 602, 102, 'Registered'),   -- Arjun registered Robotics Workshop
(803, 603, 103, 'Attended'),     -- Simran attended Cultural Fest
(804, 604, 104, 'Cancelled'),    -- Vikram cancelled Football Match
(805, 605, 105, 'Registered');   -- Ananya registered Data Science Seminar

USE AlumniDB;

DROP TRIGGER IF EXISTS before_event_insert;
DROP FUNCTION IF EXISTS mentorship_duration;
DROP FUNCTION IF EXISTS total_events_attended;
DROP PROCEDURE IF EXISTS update_alumni_company;
DROP PROCEDURE IF EXISTS list_mentorships_by_alumni;

-- =====================================================
--  Trigger
-- =====================================================
-- 1. Prevent inserting events with invalid dates
DELIMITER //
CREATE TRIGGER before_event_insert
BEFORE INSERT ON Event
FOR EACH ROW
BEGIN
    IF NEW.date < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Event date cannot be in the past';
    END IF;
END //
DELIMITER ;
INSERT INTO Event VALUES (608, 'Tech Fest', 'Inter college fest', 'Auditorium', '2023-01-01');
INSERT INTO Event VALUES (609, ' Game Development Workshop', 'Workshop for freshers', 'Auditorium', '2025-12-01');


-- =====================================================
-- FUNCTIONS
-- =====================================================
-- 1. Mentorship duration in days
DELIMITER //
CREATE FUNCTION mentorship_duration(start_date DATE, end_date DATE)
RETURNS INT
DETERMINISTIC
BEGIN
    RETURN DATEDIFF(end_date, start_date);
END //
DELIMITER ;
SELECT mid, mentorship_duration(start_date, end_date) AS DurationDays
FROM Mentorship;

-- 2. Count total events attended by an alumni
DELIMITER // -- DONE
CREATE FUNCTION total_events_attended(alumniId INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE countAttended INT;
    SELECT COUNT(*) INTO countAttended
    FROM EventParticipationAlumni
    WHERE alumni_id = alumniId AND resp_status = 'Attended';
    RETURN countAttended;
END //
DELIMITER ;
SELECT name, total_events_attended(alumni_id) AS Events_Attended
FROM Alumni;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================
-- 1. Update alumni company
DELIMITER //
CREATE PROCEDURE update_alumni_company(
    IN alumniId INT,
    IN newCompany VARCHAR(100)
)
BEGIN
    UPDATE Alumni
    SET company = newCompany
    WHERE alumni_id = alumniId;
END //
DELIMITER ;
CALL update_alumni_company(101, 'Wipro');
SELECT alumni_id, name, company FROM Alumni WHERE alumni_id = 101;

-- 2. List of students mentored by alumni -- DONE
DELIMITER //
CREATE PROCEDURE list_mentorships_by_alumni(IN alumniId INT)
BEGIN
    SELECT m.mid, s.name AS student_name, m.start_date, m.end_date
    FROM Mentorship m
    JOIN Student s ON m.student_id = s.student_id
    WHERE m.alumni_id = alumniId;
END //
DELIMITER ;
CALL list_mentorships_by_alumni(101);

-- 3. Update email and/or phone number of an alumni
DELIMITER //
CREATE PROCEDURE update_alumni_contact(
    IN a_id INT,
    IN new_email VARCHAR(100),
    IN new_phone VARCHAR(20)
)
BEGIN
    UPDATE Alumni
    SET 
        email = COALESCE(NULLIF(new_email, ''), email),
        phone_number = COALESCE(NULLIF(new_phone, ''), phone_number)
    WHERE alumni_id = a_id;
END //
DELIMITER ;

-- =====================================================
-- JOIN QUERY
-- =====================================================
SELECT
	A.name AS Alumni_Name,
	A.company AS Company,
	D.name AS Department_Name,
	A.graduation_year AS Graduation_Year,
	E.college_name AS College_Name,
	E.degree AS Degree,
	E.course AS Course
FROM Alumni A
INNER JOIN Education E ON A.alumni_id = E.alumni_id
LEFT JOIN Department D ON A.dept_id = D.dept_id
ORDER BY A.name;

-- =====================================================
-- NESTED QUERY
-- =====================================================
SELECT alumni_id, name, email
FROM Alumni
WHERE alumni_id IN (
    SELECT alumni_id
    FROM EventParticipationAlumni
    WHERE event_id = (
        SELECT event_id
        FROM Event
        WHERE name = 'Math Workshop'
    )
)
ORDER BY name;

-- =====================================================
-- AGGREGATE QUERY
-- =====================================================
-- 1. To count the number of alumni working for a particular company
SELECT company, COUNT(*) AS Alumni_Working
FROM Alumni GROUP BY company;
-- HAVING COUNT(*) > 1;

-- 2. To find the total number of people participating in an event
SELECT e.event_id,
       e.name AS Event_Name,
       (SELECT COUNT(*)
        FROM EventParticipationStudent eps
        WHERE eps.event_id = e.event_id AND eps.resp_status = 'Attended')
       +
       (SELECT COUNT(*)
        FROM EventParticipationAlumni epa
        WHERE epa.event_id = e.event_id AND epa.resp_status = 'Attended')
       AS Total_Attendees
FROM Event e;

-- ===========================================================
-- to display the name only once per alumni when viewing
SELECT
    CASE 
        WHEN @prev_name = A.name THEN ''
        ELSE A.name
    END AS Alumni_Name,
    @prev_name := A.name AS ignore_me,
    E.edu_id,
    E.college_name,
    E.degree,
    E.course,
    E.start_year,
    E.end_year
FROM Alumni A
JOIN Education E ON A.alumni_id = E.alumni_id,
(SELECT @prev_name := '') AS vars
ORDER BY A.name, E.edu_id;

-- =====================================================
-- USER PRIVILEGES
-- =====================================================
CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'admin@123'; 
CREATE USER IF NOT EXISTS 'student'@'localhost' IDENTIFIED BY 'student@123'; 
CREATE USER IF NOT EXISTS 'alumni'@'localhost' IDENTIFIED BY 'alumni@123'; 
-- Admin: Full access 
GRANT ALL PRIVILEGES ON AlumniDB.* TO 'admin'@'localhost'; 
-- Student: Read-only access 
GRANT SELECT ON AlumniDB.* TO 'student'@'localhost'; 
-- Alumni: Full Mentorship control + Read-only for all other tables 
GRANT SELECT ON AlumniDB.Department TO 'alumni'@'localhost'; 
GRANT SELECT ON AlumniDB.Alumni TO 'alumni'@'localhost'; 
GRANT SELECT ON AlumniDB.Student TO 'alumni'@'localhost'; 
GRANT SELECT ON AlumniDB.Education TO 'alumni'@'localhost'; 
GRANT SELECT ON AlumniDB.Event TO 'alumni'@'localhost'; 
GRANT SELECT ON AlumniDB.Committee TO 'alumni'@'localhost'; 
GRANT SELECT ON AlumniDB.EventParticipationStudent TO 'alumni'@'localhost'; 
GRANT SELECT ON AlumniDB.EventParticipationAlumni TO 'alumni'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON AlumniDB.Mentorship TO 'alumni'@'localhost'; 

GRANT EXECUTE ON FUNCTION AlumniDB.mentorship_duration TO 'alumni'@'localhost';
GRANT EXECUTE ON PROCEDURE AlumniDB.list_mentorships_by_alumni TO 'alumni'@'localhost';
GRANT EXECUTE ON FUNCTION AlumniDB.total_events_attended TO 'alumni'@'localhost';


FLUSH PRIVILEGES;


