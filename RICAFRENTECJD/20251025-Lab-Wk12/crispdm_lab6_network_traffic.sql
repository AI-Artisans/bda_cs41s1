-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: crispdm_lab6
-- ------------------------------------------------------
-- Server version	9.5.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'f000c54f-b16a-11f0-9c68-6ad1d7c14512:1-5';

--
-- Table structure for table `network_traffic`
--

DROP TABLE IF EXISTS `network_traffic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `network_traffic` (
  `id` int NOT NULL AUTO_INCREMENT,
  `timestamp` datetime DEFAULT NULL,
  `source_port` int DEFAULT NULL,
  `destination_port` int DEFAULT NULL,
  `protocol` varchar(10) DEFAULT NULL,
  `packet_length` int DEFAULT NULL,
  `packet_type` varchar(50) DEFAULT NULL,
  `traffic_type` varchar(50) DEFAULT NULL,
  `network_segment` varchar(50) DEFAULT NULL,
  `geo_location_data` varchar(100) DEFAULT NULL,
  `log_source` varchar(50) DEFAULT NULL,
  `source_port_orig` int DEFAULT NULL,
  `destination_port_orig` int DEFAULT NULL,
  `packet_length_orig` int DEFAULT NULL,
  `anomaly_scores_orig` float DEFAULT NULL,
  `user_anon` varchar(50) DEFAULT NULL,
  `proxy_present` tinyint(1) DEFAULT NULL,
  `proxy_hash` varchar(50) DEFAULT NULL,
  `src_ip_bucket` int DEFAULT NULL,
  `src_ip_private` tinyint(1) DEFAULT NULL,
  `dst_ip_bucket` int DEFAULT NULL,
  `dst_ip_private` tinyint(1) DEFAULT NULL,
  `src_port_bucket` varchar(50) DEFAULT NULL,
  `dst_port_bucket` varchar(50) DEFAULT NULL,
  `packet_length2` int DEFAULT NULL,
  `packet_length_log1p` float DEFAULT NULL,
  `payload_len` int DEFAULT NULL,
  `payload_url_count` int DEFAULT NULL,
  `payload_ip_count` int DEFAULT NULL,
  `payload_suspect_count` int DEFAULT NULL,
  `ua_browser` varchar(50) DEFAULT NULL,
  `attack_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2024 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `network_traffic`
--

LOCK TABLES `network_traffic` WRITE;
/*!40000 ALTER TABLE `network_traffic` DISABLE KEYS */;
INSERT INTO `network_traffic` VALUES (2020,'0000-00-00 00:00:00',48166,0,'1174',0,'Http','Segment B','Bilaspur, Nagaland','Firewall','17245',48166,1174,52,0,'False',-1,'140',0,127,0,0,'registered','1174',7,196,0,0,0,0,'Malware\r',NULL),(2021,'0000-00-00 00:00:00',50039,0,'224',0,'Http','Segment A','Rampur, Mizoram','Server','37918',50039,224,17,0,'True',127,'233',0,96,0,0,'ephemeral','224',5,131,0,0,0,0,'Malware\r',NULL),(2022,'0000-00-00 00:00:00',53600,0,'306',0,'Http','Segment C','Bokaro, Rajasthan','Firewall','16811',53600,306,87,991089,'True',127,'175',0,37,0,0,'ephemeral','306',6,76,0,0,0,0,'DDoS\r',NULL),(2023,'0000-00-00 00:00:00',17616,0,'503',0,'Http','Segment A','Jamshedpur, Sikkim','Server','31225',17616,503,29,0,'True',126,'11',0,1,0,0,'registered','503',6,165,0,0,0,0,'Malware\r',NULL);
/*!40000 ALTER TABLE `network_traffic` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-25 16:07:24
