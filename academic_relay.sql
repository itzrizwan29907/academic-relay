-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 21, 2026 at 04:34 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `academic_relay`
--

-- --------------------------------------------------------

--
-- Table structure for table `assignments`
--

CREATE TABLE `assignments` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `branch` varchar(50) NOT NULL,
  `semester` int(11) NOT NULL,
  `subject` varchar(100) NOT NULL,
  `total_questions` int(11) DEFAULT 5,
  `deadline` date NOT NULL,
  `total_marks` int(11) DEFAULT 100,
  `attachment` varchar(500) DEFAULT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `date_posted` datetime NOT NULL,
  `status` enum('active','expired') DEFAULT 'active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `assignments`
--

INSERT INTO `assignments` (`id`, `title`, `description`, `branch`, `semester`, `subject`, `total_questions`, `deadline`, `total_marks`, `attachment`, `created_by`, `created_by_id`, `date_posted`, `status`) VALUES
(1, 'CNS Assignment-02 for MID SEM-II', 'Here are the assignment-02 questions for the MID SEM-II from Unit-3 and 4. Just write them in your assignment book and make sure to submit your assignment books before deadline... 1. What is a Cryptographic Hash function? 2. Explain the Message\r\n\r\nAuthentication Code (MAC) with neat diagram. 3. Explain the Web security and threats.', 'CSE', 5, 'Cryptography & Network Security', 3, '2026-04-24', 15, NULL, 'here.is.rizwan.2007@gmail.com', 2, '2026-04-21 10:49:29', 'active'),
(2, 'Python Programming Assignment-03 for SEM END ', 'Here are the Assignment–02 questions for the MID SEM–II from Unit–5 (Python – Tkinter GUI). Just write them in your assignment book and make sure to submit your assignment books before the deadline.\r\n\r\n1. Define Tkinter. Explain the steps to create a GUI application in Python.\r\n2. Explain any five widgets in Tkinter with syntax and example.\r\n3. Explain different geometry managers (pack(), grid(), place()) with example.\r\n4. Design a login form using Tkinter and validate username and password.\r\n5. Create a GUI application to perform addition of two numbers and display the result.', 'CSE', 5, 'Python Programming', 5, '2026-04-22', 25, NULL, 'here.is.rizwan.2007@gmail.com', 2, '2026-04-21 11:03:12', 'active');

-- --------------------------------------------------------

--
-- Table structure for table `circulars`
--

CREATE TABLE `circulars` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `type` varchar(50) NOT NULL,
  `audience` varchar(100) NOT NULL,
  `priority` varchar(20) DEFAULT 'medium',
  `valid_until` date DEFAULT NULL,
  `attachment` varchar(500) DEFAULT NULL,
  `date_posted` datetime NOT NULL,
  `posted_by` varchar(100) NOT NULL,
  `posted_by_id` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `circulars`
--

INSERT INTO `circulars` (`id`, `title`, `description`, `type`, `audience`, `priority`, `valid_until`, `attachment`, `date_posted`, `posted_by`, `posted_by_id`, `is_active`) VALUES
(1, '3-Day Training Programme on Frontend Development with JavaScript', 'This is to inform you that a 3-Day Training Programme on \"Front End Development with JavaScript\" will be conducted for III Diploma V Semester students from 16th March to 18th March 2026. The training programme aims to provide students with practical knowledge and hands-on experience in front-end web development using JavaScript. This programme will help students understand modern web development concepts and improve their technical skills required for building interactive web applications. All the III Diploma V Semester students are hereby instructed to attend the training programme without fail and make the best use of this opportunity.\r\n\r\nFurther details regarding the schedule and venue will be communicated by the department.', 'event', 'students', 'high', '2026-04-22', 'WhatsApp_Image_2026-03-12_at_3.53.23_PM.jpeg', '2026-04-21 10:43:08', 'here.is.rizwan.2007@gmail.com', 2, 1),
(2, 'Diploma Examination Hall Tickets – Official Announcement', 'All diploma students are hereby informed that the Semester Examination Hall Tickets have been released.\r\n\r\nStudents are advised to download their hall tickets at the earliest from the official website:\r\n\r\nhttps://www.sbtet.telangana.gov.in\r\n\r\nImportant Instructions:\r\n\r\nCarry a printed copy of the hall ticket to the examination center.\r\nBring a valid ID proof for verification.\r\nReport to the examination center well before the scheduled time.\r\nDo not carry mobile phones or any unauthorized electronic devices.\r\n\r\nThe hall ticket is mandatory for entry into the examination hall.\r\n\r\nStudents are requested to check all details on the hall ticket carefully and report any discrepancies immediately.\r\n\r\nWishing you all the best for your examinations.', 'academic', 'students', 'urgent', '2026-04-24', 'Screenshot_2026-04-21_105916.png', '2026-04-21 11:00:01', 'here.is.rizwan.2007@gmail.com', 2, 1),
(3, 'Project work Lab External Date Released.', 'All the students are hereby informed that the Project Work Lab External date is release and it is scheduled on 21 Apr, 2026 (9:30 - 11:30). All are instructed to bring your thesis and spiral books of your respective projects...', 'academic', 'students', 'medium', '2026-04-22', NULL, '2026-04-21 11:15:20', 'faculty123@gmail.com', 7, 1);

-- --------------------------------------------------------

--
-- Table structure for table `faculty_profiles`
--

CREATE TABLE `faculty_profiles` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `department` varchar(255) DEFAULT NULL,
  `university` varchar(255) DEFAULT NULL,
  `research_interests` text DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `profile_picture` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `internal_marks`
--

CREATE TABLE `internal_marks` (
  `id` int(11) NOT NULL,
  `pin` varchar(20) NOT NULL,
  `student_name` varchar(255) NOT NULL,
  `branch` varchar(50) NOT NULL,
  `semester` int(11) NOT NULL,
  `subject_code` varchar(20) NOT NULL,
  `subject_name` varchar(255) NOT NULL,
  `marks_obtained` int(11) DEFAULT 0,
  `max_marks` int(11) DEFAULT 30,
  `uploaded_by` varchar(100) DEFAULT NULL,
  `uploaded_by_id` int(11) DEFAULT NULL,
  `date_uploaded` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `internal_marks`
--

INSERT INTO `internal_marks` (`id`, `pin`, `student_name`, `branch`, `semester`, `subject_code`, `subject_name`, `marks_obtained`, `max_marks`, `uploaded_by`, `uploaded_by_id`, `date_uploaded`) VALUES
(1, '23261-CS-033', 'Syed Rizwan', 'CSE', 5, 'ME501', 'Industrial Management & Entrepreneurship ', 20, 20, 'here.is.rizwan.2007@gmail.com', 2, '2026-04-21 10:45:36'),
(2, '23261-CS-033', 'Syed Rizwan', 'CSE', 5, 'CS503', 'Python Programming', 14, 20, 'here.is.rizwan.2007@gmail.com', 2, '2026-04-21 10:46:24'),
(3, '23261-CS-033', 'Syed Rizwan', 'CSE', 5, 'CS502', 'Web Designing', 16, 20, 'here.is.rizwan.2007@gmail.com', 2, '2026-04-21 10:46:53'),
(4, '23261-CS-033', 'Syed Rizwan', 'CSE', 5, 'CS574', '.NET Programming through C#', 11, 20, 'here.is.rizwan.2007@gmail.com', 2, '2026-04-21 10:47:19'),
(5, '23261-CS-033', 'Syed Rizwan', 'CSE', 5, 'CS585', 'Cryptography & Network Security', 7, 20, 'here.is.rizwan.2007@gmail.com', 2, '2026-04-21 10:47:46');

-- --------------------------------------------------------

--
-- Table structure for table `student_profiles`
--

CREATE TABLE `student_profiles` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `school_name` varchar(255) DEFAULT NULL,
  `grade_level` varchar(50) DEFAULT NULL,
  `academic_interests` text DEFAULT NULL,
  `bio` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `study_materials`
--

CREATE TABLE `study_materials` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `filename` varchar(500) NOT NULL,
  `original_filename` varchar(500) NOT NULL,
  `file_size` int(11) DEFAULT NULL,
  `file_type` varchar(100) DEFAULT NULL,
  `branch` varchar(50) NOT NULL,
  `semester` int(11) DEFAULT NULL,
  `subject_code` varchar(50) DEFAULT NULL,
  `subject_name` varchar(255) DEFAULT NULL,
  `uploaded_by` varchar(100) DEFAULT NULL,
  `uploaded_by_id` int(11) DEFAULT NULL,
  `date_uploaded` datetime NOT NULL,
  `download_count` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `study_materials`
--

INSERT INTO `study_materials` (`id`, `title`, `description`, `filename`, `original_filename`, `file_size`, `file_type`, `branch`, `semester`, `subject_code`, `subject_name`, `uploaded_by`, `uploaded_by_id`, `date_uploaded`, `download_count`) VALUES
(1, 'Cryptography & Network Security', 'Here are the notes of unit-01: Introduction to Cryptography.', 'CNS_unit_-_1_20260421_105123.pdf', 'CNS unit - 1.pdf', 28380971, 'application/pdf', 'CSE', 5, 'CS585', 'Cryptography & Network Security', 'here.is.rizwan.2007@gmail.com', 2, '2026-04-21 10:51:23', 2),
(2, 'Industrial Management & Entrepreneurship ', 'Here is the handout for IME (Unit-05)', 'IME_Unit_-_5_Handout_20260421_105402.pdf', 'IME Unit - 5 (Handout).pdf', 4337159, 'application/pdf', 'CSE', 5, 'ME501', 'Industrial Management & Entrepreneurship ', 'here.is.rizwan.2007@gmail.com', 2, '2026-04-21 10:54:02', 5);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `user_type` enum('student','faculty','admin') DEFAULT 'student',
  `full_name` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_active` tinyint(1) DEFAULT 1,
  `last_login` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password`, `user_type`, `full_name`, `created_at`, `updated_at`, `is_active`, `last_login`) VALUES
(1, 'itzrizwan29907@gmail.com', 'scrypt:32768:8:1$8bPQhGcu4f0WSUOY$b719c14a63ed14845712da42bbe2d3440b96fd287ee5892ff52fcdcdb4df6c57f3beb701b472886694196d9fa95afe5ec234bc458f7b668cb4c3b9c20aa6c312', 'student', NULL, '2026-04-21 05:08:24', '2026-04-21 05:08:24', 1, NULL),
(2, 'here.is.rizwan.2007@gmail.com', 'scrypt:32768:8:1$wYSRtuJFTgm0jTod$2298a1f4d88ab6e8c87d1fb4974d5967023c95a17fb4dbceb678e637bf938cdac777febce49a1982b9bf0012df7072f1a827297342913c1b4f427c2c118294c7', 'faculty', NULL, '2026-04-21 05:09:11', '2026-04-21 05:09:11', 1, NULL),
(3, 'navyasrimuraboyana2906@gmail.com', 'scrypt:32768:8:1$LK9b6DZDKJfswyhj$b67ab08e802d41ba64bfb0378d7a182fcce94b52c14d59e919914e31a7058c9b995e70d8f81402d748667fc759c54ff6a89e36c9f1f99add359d06d63e6c9954', 'student', NULL, '2026-04-21 05:38:40', '2026-04-21 05:38:40', 1, NULL),
(4, 'chraviteja001@gmail.com', 'scrypt:32768:8:1$viuvuscJWoFLF3oK$9c92e20ffa4c47786b1e5d115af3cea55f5f8f945671414f38888aa7600e03e6829bc05c73fd79a53ff0e728f80f48df9e7131cd7aca5b92a29f5bd95f3bba37', 'student', NULL, '2026-04-21 05:39:11', '2026-04-21 05:39:11', 1, NULL),
(5, 'dhavalmishra126@gmail.com', 'scrypt:32768:8:1$oM0CuMSxAhc1dhQC$124e61c69417798ccdcbb1843945bfddc7d14ee1c84767a2fd074ee7b0735ed21a93a5b6b43ad212b92a6a89afdd618f559a11b8e52b4db9ac8cc256f7e46a33', 'student', NULL, '2026-04-21 05:39:38', '2026-04-21 05:39:38', 1, NULL),
(6, 'abhinay123@gmail.com', 'scrypt:32768:8:1$gxnUqt4T1LHwDqgN$8e73b87b0420667b123448c4666c7553de0c4056da6c75856a0c2bc3fa8a3d849b08031db352bdc24a400be0b4a6383c3c07db1227bd9a66a87368b6f6991371', 'student', NULL, '2026-04-21 05:40:02', '2026-04-21 05:40:02', 1, NULL),
(7, 'faculty123@gmail.com', 'scrypt:32768:8:1$MbdJtMRLwGQPD8QE$8ec9d183ed10f5366fa9dfeeaa0c6c6e6fa4a4a01239da6a4e23da8887e980cca6859fdeac7579ed2e4e3fab60e049a3783653faee334cbf11fee87f74ec873d', 'faculty', NULL, '2026-04-21 05:40:28', '2026-04-21 05:40:28', 1, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `assignments`
--
ALTER TABLE `assignments`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `circulars`
--
ALTER TABLE `circulars`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `faculty_profiles`
--
ALTER TABLE `faculty_profiles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `internal_marks`
--
ALTER TABLE `internal_marks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `pin` (`pin`);

--
-- Indexes for table `student_profiles`
--
ALTER TABLE `student_profiles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `study_materials`
--
ALTER TABLE `study_materials`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_branch` (`branch`),
  ADD KEY `idx_semester` (`semester`),
  ADD KEY `idx_subject_code` (`subject_code`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `assignments`
--
ALTER TABLE `assignments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `circulars`
--
ALTER TABLE `circulars`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `faculty_profiles`
--
ALTER TABLE `faculty_profiles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `internal_marks`
--
ALTER TABLE `internal_marks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `student_profiles`
--
ALTER TABLE `student_profiles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `study_materials`
--
ALTER TABLE `study_materials`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
