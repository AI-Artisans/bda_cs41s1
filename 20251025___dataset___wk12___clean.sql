-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 07, 2025 at 05:31 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `lab_week12`
--

-- --------------------------------------------------------

--
-- Table structure for table `20251025___dataset___wk12___clean`
--

CREATE TABLE `20251025___dataset___wk12___clean` (
  `Timestamp` varchar(19) DEFAULT NULL,
  `Source IP Address` varchar(15) DEFAULT NULL,
  `Destination IP Address` varchar(15) DEFAULT NULL,
  `Source Port` int(5) DEFAULT NULL,
  `Destination Port` int(5) DEFAULT NULL,
  `Protocol` varchar(4) DEFAULT NULL,
  `Packet Length` int(4) DEFAULT NULL,
  `Packet Type` varchar(7) DEFAULT NULL,
  `Traffic Type` varchar(4) DEFAULT NULL,
  `Attack Type` varchar(9) DEFAULT NULL,
  `Attack Signature` varchar(15) DEFAULT NULL,
  `Action Taken` varchar(7) DEFAULT NULL,
  `Severity Level` varchar(6) DEFAULT NULL,
  `User Information` varchar(25) DEFAULT NULL,
  `Device Information` varchar(147) DEFAULT NULL,
  `Network Segment` varchar(9) DEFAULT NULL,
  `Geo-location Data` varchar(47) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
