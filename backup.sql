-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: petro_db
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts_customuser`
--

DROP TABLE IF EXISTS `accounts_customuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_customuser` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` longtext COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_customuser`
--

LOCK TABLES `accounts_customuser` WRITE;
/*!40000 ALTER TABLE `accounts_customuser` DISABLE KEYS */;
INSERT INTO `accounts_customuser` VALUES (1,'pbkdf2_sha256$1000000$ZAlLSEMBSvpF0Ga8EQQbGo$MPSm0OewScXuZNCaCzUFQJxMQG/BSrU/eebOX0CubZs=','2025-11-08 05:52:00.595267',1,'sitep','','','imedmy@gmail.com',1,1,'2025-08-13 08:51:36.984771','93242069','None','2025-08-13 08:51:37.500012','2025-08-15 08:06:56.881256'),(3,'pbkdf2_sha256$1000000$ZHGFDXY2A3kfLdMVik9Dq9$GgjBQwJVJwn1eA9/JCdBwhy+SqeyOiTcH8I3mPiLdvw=',NULL,0,'1815','ImedEddine','Elmekki','Imed@sitep.com.tn',1,1,'2025-11-07 17:11:54.000000','',NULL,'2025-11-07 17:11:54.000000','2025-11-07 17:11:54.000000');
/*!40000 ALTER TABLE `accounts_customuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_customuser_groups`
--

DROP TABLE IF EXISTS `accounts_customuser_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_customuser_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_customuser_groups_customuser_id_group_id_c074bdcb_uniq` (`customuser_id`,`group_id`),
  KEY `accounts_customuser_groups_group_id_86ba5f9e_fk_auth_group_id` (`group_id`),
  CONSTRAINT `accounts_customuser__customuser_id_bc55088e_fk_accounts_` FOREIGN KEY (`customuser_id`) REFERENCES `accounts_customuser` (`id`),
  CONSTRAINT `accounts_customuser_groups_group_id_86ba5f9e_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_customuser_groups`
--

LOCK TABLES `accounts_customuser_groups` WRITE;
/*!40000 ALTER TABLE `accounts_customuser_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_customuser_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_customuser_user_permissions`
--

DROP TABLE IF EXISTS `accounts_customuser_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_customuser_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_customuser_user_customuser_id_permission_9632a709_uniq` (`customuser_id`,`permission_id`),
  KEY `accounts_customuser__permission_id_aea3d0e5_fk_auth_perm` (`permission_id`),
  CONSTRAINT `accounts_customuser__customuser_id_0deaefae_fk_accounts_` FOREIGN KEY (`customuser_id`) REFERENCES `accounts_customuser` (`id`),
  CONSTRAINT `accounts_customuser__permission_id_aea3d0e5_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_customuser_user_permissions`
--

LOCK TABLES `accounts_customuser_user_permissions` WRITE;
/*!40000 ALTER TABLE `accounts_customuser_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_customuser_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=169 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add مستخدم',6,'add_customuser'),(22,'Can change مستخدم',6,'change_customuser'),(23,'Can delete مستخدم',6,'delete_customuser'),(24,'Can view مستخدم',6,'view_customuser'),(25,'Can add معلومات الشركة',7,'add_companyinfo'),(26,'Can change معلومات الشركة',7,'change_companyinfo'),(27,'Can delete معلومات الشركة',7,'delete_companyinfo'),(28,'Can view معلومات الشركة',7,'view_companyinfo'),(29,'Can add صفحة',8,'add_page'),(30,'Can change صفحة',8,'change_page'),(31,'Can delete صفحة',8,'delete_page'),(32,'Can view صفحة',8,'view_page'),(33,'Can add مصفوفة الصلاحيات',9,'add_permissionmatrix'),(34,'Can change مصفوفة الصلاحيات',9,'change_permissionmatrix'),(35,'Can delete مصفوفة الصلاحيات',9,'delete_permissionmatrix'),(36,'Can view مصفوفة الصلاحيات',9,'view_permissionmatrix'),(37,'Can add article',10,'add_article'),(38,'Can change article',10,'change_article'),(39,'Can delete article',10,'delete_article'),(40,'Can view article',10,'view_article'),(41,'Can add Famille d\'article',11,'add_articlefamily'),(42,'Can change Famille d\'article',11,'change_articlefamily'),(43,'Can delete Famille d\'article',11,'delete_articlefamily'),(44,'Can view Famille d\'article',11,'view_articlefamily'),(45,'Can add article sql',12,'add_articlesql'),(46,'Can change article sql',12,'change_articlesql'),(47,'Can delete article sql',12,'delete_articlesql'),(48,'Can view article sql',12,'view_articlesql'),(49,'Can add Caractéristique',13,'add_caracteristique'),(50,'Can change Caractéristique',13,'change_caracteristique'),(51,'Can delete Caractéristique',13,'delete_caracteristique'),(52,'Can view Caractéristique',13,'view_caracteristique'),(53,'Can add Image Article',14,'add_articleimage'),(54,'Can change Image Article',14,'change_articleimage'),(55,'Can delete Image Article',14,'delete_articleimage'),(56,'Can view Image Article',14,'view_articleimage'),(57,'Can add Valeur Caractéristique Article',15,'add_articlecaracteristique'),(58,'Can change Valeur Caractéristique Article',15,'change_articlecaracteristique'),(59,'Can delete Valeur Caractéristique Article',15,'delete_articlecaracteristique'),(60,'Can view Valeur Caractéristique Article',15,'view_articlecaracteristique'),(61,'Can add Unité avec Numéro de Série',16,'add_serialunit'),(62,'Can change Unité avec Numéro de Série',16,'change_serialunit'),(63,'Can delete Unité avec Numéro de Série',16,'delete_serialunit'),(64,'Can view Unité avec Numéro de Série',16,'view_serialunit'),(65,'Can add Type de Mouvement',17,'add_typemouvement'),(66,'Can change Type de Mouvement',17,'change_typemouvement'),(67,'Can delete Type de Mouvement',17,'delete_typemouvement'),(68,'Can view Type de Mouvement',17,'view_typemouvement'),(69,'Can add Nature de stock',18,'add_naturestock'),(70,'Can change Nature de stock',18,'change_naturestock'),(71,'Can delete Nature de stock',18,'delete_naturestock'),(72,'Can view Nature de stock',18,'view_naturestock'),(73,'Can add Valeur d\'article',19,'add_valeurarticle'),(74,'Can change Valeur d\'article',19,'change_valeurarticle'),(75,'Can delete Valeur d\'article',19,'delete_valeurarticle'),(76,'Can view Valeur d\'article',19,'view_valeurarticle'),(77,'Can add Étape de dossier',20,'add_etapedossier'),(78,'Can change Étape de dossier',20,'change_etapedossier'),(79,'Can delete Étape de dossier',20,'delete_etapedossier'),(80,'Can view Étape de dossier',20,'view_etapedossier'),(81,'Can add suivi dossier',21,'add_suividossier'),(82,'Can change suivi dossier',21,'change_suividossier'),(83,'Can delete suivi dossier',21,'delete_suividossier'),(84,'Can view suivi dossier',21,'view_suividossier'),(85,'Can add piece jointe etape',22,'add_piecejointeetape'),(86,'Can change piece jointe etape',22,'change_piecejointeetape'),(87,'Can delete piece jointe etape',22,'delete_piecejointeetape'),(88,'Can view piece jointe etape',22,'view_piecejointeetape'),(89,'Can add etat b1 view',23,'add_etatb1view'),(90,'Can change etat b1 view',23,'change_etatb1view'),(91,'Can delete etat b1 view',23,'delete_etatb1view'),(92,'Can view etat b1 view',23,'view_etatb1view'),(93,'Can add Avis d\'Arrivée',24,'add_avisarrivee'),(94,'Can change Avis d\'Arrivée',24,'change_avisarrivee'),(95,'Can delete Avis d\'Arrivée',24,'delete_avisarrivee'),(96,'Can view Avis d\'Arrivée',24,'view_avisarrivee'),(97,'Can add Détail Avis',25,'add_detailavis'),(98,'Can change Détail Avis',25,'change_detailavis'),(99,'Can delete Détail Avis',25,'delete_detailavis'),(100,'Can view Détail Avis',25,'view_detailavis'),(101,'Can add Pièce jointe',26,'add_piecejointeavis'),(102,'Can change Pièce jointe',26,'change_piecejointeavis'),(103,'Can delete Pièce jointe',26,'delete_piecejointeavis'),(104,'Can view Pièce jointe',26,'view_piecejointeavis'),(105,'Can add Tiers',27,'add_tiers'),(106,'Can change Tiers',27,'change_tiers'),(107,'Can delete Tiers',27,'delete_tiers'),(108,'Can view Tiers',27,'view_tiers'),(109,'Can add Engin',28,'add_engin'),(110,'Can change Engin',28,'change_engin'),(111,'Can delete Engin',28,'delete_engin'),(112,'Can view Engin',28,'view_engin'),(113,'Can add Pièce jointe',29,'add_piecejointetache'),(114,'Can change Pièce jointe',29,'change_piecejointetache'),(115,'Can delete Pièce jointe',29,'delete_piecejointetache'),(116,'Can view Pièce jointe',29,'view_piecejointetache'),(117,'Can add Intervenant',30,'add_intervenant'),(118,'Can change Intervenant',30,'change_intervenant'),(119,'Can delete Intervenant',30,'delete_intervenant'),(120,'Can view Intervenant',30,'view_intervenant'),(121,'Can add Personnel',31,'add_personnel'),(122,'Can change Personnel',31,'change_personnel'),(123,'Can delete Personnel',31,'delete_personnel'),(124,'Can view Personnel',31,'view_personnel'),(125,'Can add Tâche',32,'add_tache'),(126,'Can change Tâche',32,'change_tache'),(127,'Can delete Tâche',32,'delete_tache'),(128,'Can view Tâche',32,'view_tache'),(129,'Can add Planning Tâche (Référentiel)',33,'add_planningtache'),(130,'Can change Planning Tâche (Référentiel)',33,'change_planningtache'),(131,'Can delete Planning Tâche (Référentiel)',33,'delete_planningtache'),(132,'Can view Planning Tâche (Référentiel)',33,'view_planningtache'),(133,'Can add Point de Barremage',34,'add_barremage'),(134,'Can change Point de Barremage',34,'change_barremage'),(135,'Can delete Point de Barremage',34,'delete_barremage'),(136,'Can view Point de Barremage',34,'view_barremage'),(137,'Can add Citerne',35,'add_citerne'),(138,'Can change Citerne',35,'change_citerne'),(139,'Can delete Citerne',35,'delete_citerne'),(140,'Can view Citerne',35,'view_citerne'),(141,'Can add Consommation / Ravitaillement',36,'add_consommationcarburant'),(142,'Can change Consommation / Ravitaillement',36,'change_consommationcarburant'),(143,'Can delete Consommation / Ravitaillement',36,'delete_consommationcarburant'),(144,'Can view Consommation / Ravitaillement',36,'view_consommationcarburant'),(145,'Can add Lecture d\'index',37,'add_lectureindex'),(146,'Can change Lecture d\'index',37,'change_lectureindex'),(147,'Can delete Lecture d\'index',37,'delete_lectureindex'),(148,'Can view Lecture d\'index',37,'view_lectureindex'),(149,'Can add Lecture de Jauge',38,'add_lecturejauge'),(150,'Can change Lecture de Jauge',38,'change_lecturejauge'),(151,'Can delete Lecture de Jauge',38,'delete_lecturejauge'),(152,'Can view Lecture de Jauge',38,'view_lecturejauge'),(153,'Can add Lecture de Pompe',39,'add_lecturepompe'),(154,'Can change Lecture de Pompe',39,'change_lecturepompe'),(155,'Can delete Lecture de Pompe',39,'delete_lecturepompe'),(156,'Can view Lecture de Pompe',39,'view_lecturepompe'),(157,'Can add Équipement',40,'add_equipement'),(158,'Can change Équipement',40,'change_equipement'),(159,'Can delete Équipement',40,'delete_equipement'),(160,'Can view Équipement',40,'view_equipement'),(161,'Can add Service',41,'add_service'),(162,'Can change Service',41,'change_service'),(163,'Can delete Service',41,'delete_service'),(164,'Can view Service',41,'view_service'),(165,'Can add Notification',42,'add_notification'),(166,'Can change Notification',42,'change_notification'),(167,'Can delete Notification',42,'delete_notification'),(168,'Can view Notification',42,'view_notification');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `avis_arrivee`
--

DROP TABLE IF EXISTS `avis_arrivee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `avis_arrivee` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `numero_com` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `numero_avis` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_avis` date NOT NULL,
  `numero_bordereau` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bct` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `numero_facture` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `numero_bl` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observation` longtext COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `dat_com` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `avis_arrivee`
--

LOCK TABLES `avis_arrivee` WRITE;
/*!40000 ALTER TABLE `avis_arrivee` DISABLE KEYS */;
INSERT INTO `avis_arrivee` VALUES (5,'0013/2024E','2899','2025-10-30','29/10/2025','','WSES/1001/2025','','PV de reception en usine + Packing List\r\nReçu Conforme Selon Sce QHSE + Transport\r\nManque 2 bouteille Oxigene','2025-11-04 08:39:39.955967','2025-11-04 15:45:26.088435','2024-09-17');
/*!40000 ALTER TABLE `avis_arrivee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `barremage`
--

DROP TABLE IF EXISTS `barremage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `barremage` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `hauteur_cm` decimal(6,2) NOT NULL,
  `volume_litres` decimal(12,3) NOT NULL,
  `date_enregistrement` datetime(6) NOT NULL,
  `citerne_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `barremage_citerne_id_hauteur_cm_b79d195c_uniq` (`citerne_id`,`hauteur_cm`),
  CONSTRAINT `barremage_citerne_id_9e2addb7_fk_citerne_id` FOREIGN KEY (`citerne_id`) REFERENCES `citerne` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=644 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `barremage`
--

LOCK TABLES `barremage` WRITE;
/*!40000 ALTER TABLE `barremage` DISABLE KEYS */;
INSERT INTO `barremage` VALUES (1,1.00,8.000,'2025-11-08 13:30:37.593764',1),(2,2.00,23.000,'2025-11-08 13:30:37.708445',1),(3,3.00,42.000,'2025-11-08 13:30:37.773120',1),(4,4.00,65.000,'2025-11-08 13:30:37.832912',1),(5,5.00,91.000,'2025-11-08 13:30:37.875419',1),(6,6.00,120.000,'2025-11-08 13:30:37.942121',1),(7,7.00,152.000,'2025-11-08 13:30:37.984650',1),(8,8.00,185.000,'2025-11-08 13:30:38.076921',1),(9,9.00,221.000,'2025-11-08 13:30:38.194641',1),(10,10.00,260.000,'2025-11-08 13:30:38.316798',1),(11,11.00,300.000,'2025-11-08 13:30:38.368546',1),(12,12.00,342.000,'2025-11-08 13:30:38.435194',1),(13,13.00,385.000,'2025-11-08 13:30:38.501875',1),(14,14.00,431.000,'2025-11-08 13:30:38.543561',1),(15,15.00,478.000,'2025-11-08 13:30:38.601911',1),(16,16.00,526.000,'2025-11-08 13:30:38.643577',1),(17,17.00,577.000,'2025-11-08 13:30:38.685294',1),(18,18.00,628.000,'2025-11-08 13:30:38.726945',1),(19,19.00,681.000,'2025-11-08 13:30:38.802000',1),(20,20.00,736.000,'2025-11-08 13:30:38.843686',1),(21,21.00,791.000,'2025-11-08 13:30:38.885383',1),(22,22.00,849.000,'2025-11-08 13:30:38.943723',1),(23,23.00,907.000,'2025-11-08 13:30:39.027066',1),(24,24.00,966.000,'2025-11-08 13:30:39.068767',1),(25,25.00,1027.000,'2025-11-08 13:30:39.144215',1),(26,26.00,1089.000,'2025-11-08 13:30:39.185493',1),(27,27.00,1152.000,'2025-11-08 13:30:39.268896',1),(28,28.00,1217.000,'2025-11-08 13:30:39.310553',1),(29,29.00,1282.000,'2025-11-08 13:30:39.402349',1),(30,30.00,1348.000,'2025-11-08 13:30:39.450163',1),(31,31.00,1416.000,'2025-11-08 13:30:39.526389',1),(32,32.00,1484.000,'2025-11-08 13:30:39.593975',1),(33,33.00,1553.000,'2025-11-08 13:30:39.635711',1),(34,34.00,1624.000,'2025-11-08 13:30:39.694016',1),(35,35.00,1695.000,'2025-11-08 13:30:39.735702',1),(36,36.00,1767.000,'2025-11-08 13:30:39.802392',1),(37,37.00,1811.000,'2025-11-08 13:30:39.869120',1),(38,38.00,1915.000,'2025-11-08 13:30:39.935864',1),(39,39.00,1990.000,'2025-11-08 13:30:39.985397',1),(40,40.00,2065.000,'2025-11-08 13:30:40.027456',1),(41,41.00,2142.000,'2025-11-08 13:30:40.136402',1),(42,42.00,2219.000,'2025-11-08 13:30:40.219770',1),(43,43.00,2298.000,'2025-11-08 13:30:40.277595',1),(44,44.00,2377.000,'2025-11-08 13:30:40.319270',1),(45,45.00,2457.000,'2025-11-08 13:30:40.360991',1),(46,46.00,2537.000,'2025-11-08 13:30:40.419855',1),(47,47.00,2618.000,'2025-11-08 13:30:40.494346',1),(48,48.00,2700.000,'2025-11-08 13:30:40.536051',1),(49,49.00,2783.000,'2025-11-08 13:30:40.586144',1),(50,50.00,2867.000,'2025-11-08 13:30:40.636625',1),(51,51.00,2951.000,'2025-11-08 13:30:40.714392',1),(52,52.00,3036.000,'2025-11-08 13:30:40.786859',1),(53,53.00,3121.000,'2025-11-08 13:30:40.850062',1),(54,54.00,3207.000,'2025-11-08 13:30:40.911316',1),(55,55.00,3254.000,'2025-11-08 13:30:41.002940',1),(56,56.00,3381.000,'2025-11-08 13:30:41.043824',1),(57,57.00,3469.000,'2025-11-08 13:30:41.167250',1),(58,58.00,3558.000,'2025-11-08 13:30:41.219737',1),(59,59.00,3647.000,'2025-11-08 13:30:41.261479',1),(60,60.00,3737.000,'2025-11-08 13:30:41.353100',1),(61,61.00,3827.000,'2025-11-08 13:30:41.394794',1),(62,62.00,3918.000,'2025-11-08 13:30:41.436449',1),(63,63.00,4009.000,'2025-11-08 13:30:41.478144',1),(64,64.00,4101.000,'2025-11-08 13:30:41.544893',1),(65,65.00,4194.000,'2025-11-08 13:30:41.586543',1),(66,66.00,4287.000,'2025-11-08 13:30:41.669857',1),(67,67.00,4380.000,'2025-11-08 13:30:41.711616',1),(68,68.00,4474.000,'2025-11-08 13:30:41.778267',1),(69,69.00,4569.000,'2025-11-08 13:30:41.828753',1),(70,70.00,4664.000,'2025-11-08 13:30:41.898136',1),(71,71.00,4759.000,'2025-11-08 13:30:41.936668',1),(72,72.00,4855.000,'2025-11-08 13:30:41.978324',1),(73,73.00,4951.000,'2025-11-08 13:30:42.044063',1),(74,74.00,5048.000,'2025-11-08 13:30:42.111818',1),(75,75.00,5147.000,'2025-11-08 13:30:42.197731',1),(76,76.00,5242.000,'2025-11-08 13:30:42.236869',1),(77,77.00,5340.000,'2025-11-08 13:30:42.328497',1),(78,78.00,5438.000,'2025-11-08 13:30:42.370590',1),(79,79.00,5537.000,'2025-11-08 13:30:42.411887',1),(80,80.00,5636.000,'2025-11-08 13:30:42.487404',1),(81,81.00,5735.000,'2025-11-08 13:30:42.528553',1),(82,82.00,5835.000,'2025-11-08 13:30:42.603638',1),(83,83.00,5935.000,'2025-11-08 13:30:42.661942',1),(84,84.00,6036.000,'2025-11-08 13:30:42.736987',1),(85,85.00,6136.000,'2025-11-08 13:30:42.778645',1),(86,86.00,6237.000,'2025-11-08 13:30:42.820355',1),(87,87.00,6339.000,'2025-11-08 13:30:42.962075',1),(88,88.00,6441.000,'2025-11-08 13:30:43.003824',1),(89,89.00,6542.000,'2025-11-08 13:30:43.103858',1),(90,90.00,6645.000,'2025-11-08 13:30:43.145483',1),(91,91.00,6747.000,'2025-11-08 13:30:43.220603',1),(92,92.00,6850.000,'2025-11-08 13:30:43.278862',1),(93,93.00,6953.000,'2025-11-08 13:30:43.345616',1),(94,94.00,7056.000,'2025-11-08 13:30:43.444252',1),(95,95.00,7160.000,'2025-11-08 13:30:43.504045',1),(96,96.00,7264.000,'2025-11-08 13:30:43.570758',1),(97,97.00,7368.000,'2025-11-08 13:30:43.629043',1),(98,98.00,7472.000,'2025-11-08 13:30:43.687213',1),(99,99.00,7576.000,'2025-11-08 13:30:43.728731',1),(100,100.00,7681.000,'2025-11-08 13:30:43.770890',1),(101,101.00,7786.000,'2025-11-08 13:30:43.829073',1),(102,102.00,7891.000,'2025-11-08 13:30:43.879212',1),(103,103.00,7996.000,'2025-11-08 13:30:43.937547',1),(104,104.00,8101.000,'2025-11-08 13:30:44.004657',1),(105,105.00,8207.000,'2025-11-08 13:30:44.045884',1),(106,106.00,8312.000,'2025-11-08 13:30:44.087685',1),(107,107.00,8418.000,'2025-11-08 13:30:44.154269',1),(108,108.00,8524.000,'2025-11-08 13:30:44.195949',1),(109,109.00,8630.000,'2025-11-08 13:30:44.237626',1),(110,110.00,8736.000,'2025-11-08 13:30:44.279358',1),(111,111.00,8842.000,'2025-11-08 13:30:44.321071',1),(112,112.00,8949.000,'2025-11-08 13:30:44.379353',1),(113,113.00,9055.000,'2025-11-08 13:30:44.421104',1),(114,114.00,9162.000,'2025-11-08 13:30:44.527414',1),(115,115.00,9268.000,'2025-11-08 13:30:44.579160',1),(116,116.00,9375.000,'2025-11-08 13:30:44.654507',1),(117,117.00,9482.000,'2025-11-08 13:30:44.735579',1),(118,118.00,9589.000,'2025-11-08 13:30:44.779554',1),(119,119.00,9695.000,'2025-11-08 13:30:44.821235',1),(120,120.00,9802.000,'2025-11-08 13:30:44.905127',1),(121,121.00,9909.000,'2025-11-08 13:30:44.946323',1),(122,122.00,10016.000,'2025-11-08 13:30:45.012982',1),(123,123.00,10123.000,'2025-11-08 13:30:45.054661',1),(124,124.00,10230.000,'2025-11-08 13:30:45.096390',1),(125,125.00,10337.000,'2025-11-08 13:30:45.163025',1),(126,126.00,10444.000,'2025-11-08 13:30:45.204713',1),(127,127.00,10551.000,'2025-11-08 13:30:45.271428',1),(128,128.00,10668.000,'2025-11-08 13:30:45.353273',1),(129,129.00,10765.000,'2025-11-08 13:30:45.421968',1),(130,130.00,10872.000,'2025-11-08 13:30:45.479873',1),(131,131.00,10979.000,'2025-11-08 13:30:45.522016',1),(132,132.00,11086.000,'2025-11-08 13:30:45.563271',1),(133,133.00,11193.000,'2025-11-08 13:30:45.621656',1),(134,134.00,11299.000,'2025-11-08 13:30:45.679927',1),(135,135.00,11406.000,'2025-11-08 13:30:45.721673',1),(136,136.00,11512.000,'2025-11-08 13:30:45.846670',1),(137,137.00,11619.000,'2025-11-08 13:30:45.905063',1),(138,138.00,11725.000,'2025-11-08 13:30:45.996725',1),(139,139.00,11836.000,'2025-11-08 13:30:46.063486',1),(140,140.00,11937.000,'2025-11-08 13:30:46.130135',1),(141,141.00,12043.000,'2025-11-08 13:30:46.195892',1),(142,142.00,12149.000,'2025-11-08 13:30:46.261051',1),(143,143.00,12255.000,'2025-11-08 13:30:46.330288',1),(144,144.00,12361.000,'2025-11-08 13:30:46.371976',1),(145,145.00,12466.000,'2025-11-08 13:30:46.455285',1),(146,146.00,12571.000,'2025-11-08 13:30:46.496931',1),(147,147.00,12676.000,'2025-11-08 13:30:46.538818',1),(148,148.00,12781.000,'2025-11-08 13:30:46.622427',1),(149,149.00,12886.000,'2025-11-08 13:30:46.664066',1),(150,150.00,12993.000,'2025-11-08 13:30:46.720129',1),(151,151.00,13095.000,'2025-11-08 13:30:46.755450',1),(152,152.00,13169.000,'2025-11-08 13:30:46.813997',1),(153,153.00,13303.000,'2025-11-08 13:30:46.896313',1),(154,154.00,13407.000,'2025-11-08 13:30:46.938224',1),(155,155.00,13510.000,'2025-11-08 13:30:46.980942',1),(156,156.00,13613.000,'2025-11-08 13:30:47.022253',1),(157,157.00,13716.000,'2025-11-08 13:30:47.122240',1),(158,158.00,13819.000,'2025-11-08 13:30:47.163180',1),(159,159.00,13921.000,'2025-11-08 13:30:47.265188',1),(160,160.00,14024.000,'2025-11-08 13:30:47.331228',1),(161,161.00,14126.000,'2025-11-08 13:30:47.372353',1),(162,162.00,14227.000,'2025-11-08 13:30:47.414474',1),(163,163.00,14328.000,'2025-11-08 13:30:47.519358',1),(164,164.00,14429.000,'2025-11-08 13:30:47.555749',1),(165,165.00,14530.000,'2025-11-08 13:30:47.614197',1),(166,166.00,14630.000,'2025-11-08 13:30:47.655835',1),(167,167.00,14730.000,'2025-11-08 13:30:47.745801',1),(168,168.00,14830.000,'2025-11-08 13:30:47.789236',1),(169,169.00,14929.000,'2025-11-08 13:30:47.855895',1),(170,170.00,15028.000,'2025-11-08 13:30:47.948265',1),(171,171.00,15127.000,'2025-11-08 13:30:47.989257',1),(172,172.00,15225.000,'2025-11-08 13:30:48.064976',1),(173,173.00,15323.000,'2025-11-08 13:30:48.106036',1),(174,174.00,15420.000,'2025-11-08 13:30:48.147446',1),(175,175.00,15517.000,'2025-11-08 13:30:48.213894',1),(176,176.00,15613.000,'2025-11-08 13:30:48.255364',1),(177,177.00,15709.000,'2025-11-08 13:30:48.339190',1),(178,178.00,15805.000,'2025-11-08 13:30:48.397452',1),(179,179.00,15900.000,'2025-11-08 13:30:48.438809',1),(180,180.00,15995.000,'2025-11-08 13:30:48.547992',1),(181,181.00,16089.000,'2025-11-08 13:30:48.634650',1),(182,182.00,16183.000,'2025-11-08 13:30:48.682012',1),(183,183.00,16276.000,'2025-11-08 13:30:48.739660',1),(184,184.00,16369.000,'2025-11-08 13:30:48.839522',1),(185,185.00,16462.000,'2025-11-08 13:30:48.941896',1),(186,186.00,16553.000,'2025-11-08 13:30:48.980732',1),(187,187.00,16645.000,'2025-11-08 13:30:49.061919',1),(188,188.00,16735.000,'2025-11-08 13:30:49.106531',1),(189,189.00,16825.000,'2025-11-08 13:30:49.206654',1),(190,190.00,16915.000,'2025-11-08 13:30:49.272815',1),(191,191.00,17064.000,'2025-11-08 13:30:49.314364',1),(192,192.00,17097.000,'2025-11-08 13:30:49.464652',1),(193,193.00,17180.000,'2025-11-08 13:30:49.589220',1),(194,194.00,17267.000,'2025-11-08 13:30:49.631479',1),(195,195.00,17354.000,'2025-11-08 13:30:49.748671',1),(196,196.00,17440.000,'2025-11-08 13:30:49.831172',1),(197,197.00,17525.000,'2025-11-08 13:30:49.970442',1),(198,198.00,17610.000,'2025-11-08 13:30:50.107321',1),(199,199.00,17694.000,'2025-11-08 13:30:50.148638',1),(200,200.00,17777.000,'2025-11-08 13:30:50.215751',1),(201,201.00,17859.000,'2025-11-08 13:30:50.351233',1),(202,202.00,17911.000,'2025-11-08 13:30:50.479744',1),(203,203.00,18022.000,'2025-11-08 13:30:50.560003',1),(204,204.00,18103.000,'2025-11-08 13:30:50.632332',1),(205,205.00,18182.000,'2025-11-08 13:30:50.715489',1),(206,206.00,18261.000,'2025-11-08 13:30:50.816672',1),(207,207.00,18339.000,'2025-11-08 13:30:50.924062',1),(208,208.00,18416.000,'2025-11-08 13:30:51.047448',1),(209,209.00,18493.000,'2025-11-08 13:30:51.115054',1),(210,210.00,18568.000,'2025-11-08 13:30:51.235028',1),(211,211.00,18643.000,'2025-11-08 13:30:51.337115',1),(212,212.00,18717.000,'2025-11-08 13:30:51.380317',1),(213,213.00,18789.000,'2025-11-08 13:30:51.456554',1),(214,214.00,18861.000,'2025-11-08 13:30:51.523559',1),(215,215.00,18932.000,'2025-11-08 13:30:51.565804',1),(216,216.00,19003.000,'2025-11-08 13:30:51.633883',1),(217,217.00,19072.000,'2025-11-08 13:30:51.682547',1),(218,218.00,19140.000,'2025-11-08 13:30:51.782554',1),(219,219.00,19207.000,'2025-11-08 13:30:51.849242',1),(220,220.00,19273.000,'2025-11-08 13:30:51.890921',1),(221,221.00,19338.000,'2025-11-08 13:30:51.957546',1),(222,222.00,19402.000,'2025-11-08 13:30:51.999338',1),(223,223.00,19464.000,'2025-11-08 13:30:52.058210',1),(224,224.00,19526.000,'2025-11-08 13:30:52.123799',1),(225,225.00,19586.000,'2025-11-08 13:30:52.165271',1),(226,226.00,19646.000,'2025-11-08 13:30:52.232779',1),(227,227.00,19704.000,'2025-11-08 13:30:52.274421',1),(228,228.00,19760.000,'2025-11-08 13:30:52.316156',1),(229,229.00,19816.000,'2025-11-08 13:30:52.382545',1),(230,230.00,19870.000,'2025-11-08 13:30:52.424526',1),(231,231.00,19922.000,'2025-11-08 13:30:52.466271',1),(232,232.00,19973.000,'2025-11-08 13:30:52.563714',1),(233,233.00,20023.000,'2025-11-08 13:30:52.632951',1),(234,234.00,20071.000,'2025-11-08 13:30:52.724628',1),(235,235.00,20118.000,'2025-11-08 13:30:52.766280',1),(236,236.00,20163.000,'2025-11-08 13:30:52.841407',1),(237,237.00,20206.000,'2025-11-08 13:30:52.899709',1),(238,238.00,20247.000,'2025-11-08 13:30:53.022968',1),(239,239.00,20287.000,'2025-11-08 13:30:53.071369',1),(240,240.00,20324.000,'2025-11-08 13:30:53.153968',1),(241,0.00,0.000,'2025-11-08 13:46:38.844857',2),(242,1.00,16.600,'2025-11-08 13:46:38.900932',2),(243,2.00,46.900,'2025-11-08 13:46:38.998467',2),(244,3.00,85.900,'2025-11-08 13:46:39.125916',2),(245,4.00,132.000,'2025-11-08 13:46:39.168100',2),(246,5.00,184.100,'2025-11-08 13:46:39.226322',2),(247,6.00,241.600,'2025-11-08 13:46:39.267638',2),(248,7.00,303.900,'2025-11-08 13:46:39.308492',2),(249,8.00,370.600,'2025-11-08 13:46:39.367658',2),(250,9.00,441.400,'2025-11-08 13:46:39.409349',2),(251,10.00,516.100,'2025-11-08 13:46:39.467710',2),(252,11.00,594.300,'2025-11-08 13:46:39.509391',2),(253,12.00,676.000,'2025-11-08 13:46:39.567713',2),(254,13.00,760.900,'2025-11-08 13:46:39.609382',2),(255,14.00,848.900,'2025-11-08 13:46:39.651110',2),(256,15.00,939.900,'2025-11-08 13:46:39.692773',2),(257,16.00,1033.600,'2025-11-08 13:46:39.734414',2),(258,17.00,1130.100,'2025-11-08 13:46:39.792774',2),(259,18.00,1229.100,'2025-11-08 13:46:39.834431',2),(260,19.00,1330.600,'2025-11-08 13:46:39.876125',2),(261,20.00,1434.500,'2025-11-08 13:46:39.917809',2),(262,21.00,1540.800,'2025-11-08 13:46:39.959646',2),(263,22.00,1679.200,'2025-11-08 13:46:40.017896',2),(264,23.00,1759.800,'2025-11-08 13:46:40.059584',2),(265,24.00,1872.600,'2025-11-08 13:46:40.117983',2),(266,25.00,1987.300,'2025-11-08 13:46:40.159632',2),(267,26.00,2104.000,'2025-11-08 13:46:40.201296',2),(268,27.00,2222.600,'2025-11-08 13:46:40.242980',2),(269,28.00,2343.000,'2025-11-08 13:46:40.315495',2),(270,29.00,2465.300,'2025-11-08 13:46:40.384699',2),(271,30.00,2589.200,'2025-11-08 13:46:40.443066',2),(272,31.00,2714.900,'2025-11-08 13:46:40.484742',2),(273,32.00,2842.200,'2025-11-08 13:46:40.526396',2),(274,33.00,2971.000,'2025-11-08 13:46:40.576434',2),(275,34.00,3101.500,'2025-11-08 13:46:40.618116',2),(276,35.00,3233.400,'2025-11-08 13:46:40.765288',2),(277,36.00,3366.800,'2025-11-08 13:46:40.801536',2),(278,37.00,3501.600,'2025-11-08 13:46:40.860266',2),(279,38.00,3637.800,'2025-11-08 13:46:40.926151',2),(280,39.00,3775.400,'2025-11-08 13:46:40.976598',2),(281,40.00,3914.200,'2025-11-08 13:46:41.017483',2),(282,41.00,4054.300,'2025-11-08 13:46:41.059506',2),(283,42.00,4195.700,'2025-11-08 13:46:41.101747',2),(284,43.00,4338.300,'2025-11-08 13:46:41.162623',2),(285,44.00,4482.000,'2025-11-08 13:46:41.201678',2),(286,45.00,4626.900,'2025-11-08 13:46:41.243352',2),(287,46.00,4772.900,'2025-11-08 13:46:41.285069',2),(288,47.00,4920.000,'2025-11-08 13:46:41.326737',2),(289,48.00,5068.100,'2025-11-08 13:46:41.368465',2),(290,49.00,5217.300,'2025-11-08 13:46:41.466669',2),(291,50.00,5367.400,'2025-11-08 13:46:41.518529',2),(292,51.00,5518.500,'2025-11-08 13:46:41.560226',2),(293,52.00,5670.600,'2025-11-08 13:46:41.626902',2),(294,53.00,5823.500,'2025-11-08 13:46:41.668606',2),(295,54.00,5977.300,'2025-11-08 13:46:41.727411',2),(296,55.00,6132.000,'2025-11-08 13:46:41.768619',2),(297,56.00,6287.500,'2025-11-08 13:46:41.843651',2),(298,57.00,6443.900,'2025-11-08 13:46:41.902017',2),(299,58.00,6601.000,'2025-11-08 13:46:41.943671',2),(300,59.00,6758.800,'2025-11-08 13:46:41.985432',2),(301,60.00,6917.400,'2025-11-08 13:46:42.027085',2),(302,61.00,7076.700,'2025-11-08 13:46:42.111875',2),(303,62.00,7236.700,'2025-11-08 13:46:42.176445',2),(304,63.00,7397.300,'2025-11-08 13:46:42.218829',2),(305,64.00,7558.600,'2025-11-08 13:46:42.285529',2),(306,65.00,7720.500,'2025-11-08 13:46:42.327210',2),(307,66.00,7883.000,'2025-11-08 13:46:42.368843',2),(308,67.00,8046.000,'2025-11-08 13:46:42.427247',2),(309,68.00,8209.600,'2025-11-08 13:46:42.469276',2),(310,69.00,8373.700,'2025-11-08 13:46:42.527277',2),(311,70.00,8538.400,'2025-11-08 13:46:42.568953',2),(312,71.00,8703.500,'2025-11-08 13:46:42.685808',2),(313,72.00,8869.100,'2025-11-08 13:46:42.760703',2),(314,73.00,9035.100,'2025-11-08 13:46:42.860879',2),(315,74.00,9201.500,'2025-11-08 13:46:42.971013',2),(316,75.00,9368.400,'2025-11-08 13:46:43.010865',2),(317,76.00,9535.600,'2025-11-08 13:46:43.052498',2),(318,77.00,9703.200,'2025-11-08 13:46:43.093351',2),(319,78.00,9871.100,'2025-11-08 13:46:43.169202',2),(320,79.00,10039.300,'2025-11-08 13:46:43.211037',2),(321,80.00,10207.800,'2025-11-08 13:46:43.269293',2),(322,81.00,10376.700,'2025-11-08 13:46:43.310969',2),(323,82.00,10545.700,'2025-11-08 13:46:43.376799',2),(324,83.00,10715.000,'2025-11-08 13:46:43.418848',2),(325,84.00,10884.600,'2025-11-08 13:46:43.461017',2),(326,85.00,11054.300,'2025-11-08 13:46:43.527722',2),(327,86.00,11224.200,'2025-11-08 13:46:43.569352',2),(328,87.00,11394.300,'2025-11-08 13:46:43.611085',2),(329,88.00,11564.500,'2025-11-08 13:46:43.753217',2),(330,89.00,11734.900,'2025-11-08 13:46:43.811154',2),(331,90.00,11905.300,'2025-11-08 13:46:43.877851',2),(332,91.00,12075.800,'2025-11-08 13:46:43.936224',2),(333,92.00,12246.400,'2025-11-08 13:46:43.977890',2),(334,93.00,12417.100,'2025-11-08 13:46:44.036246',2),(335,94.00,12587.800,'2025-11-08 13:46:44.078436',2),(336,95.00,12758.400,'2025-11-08 13:46:44.118841',2),(337,96.00,12929.100,'2025-11-08 13:46:44.160892',2),(338,97.00,13099.700,'2025-11-08 13:46:44.228074',2),(339,98.00,13270.300,'2025-11-08 13:46:44.286384',2),(340,99.00,13440.800,'2025-11-08 13:46:44.353092',2),(341,100.00,13611.300,'2025-11-08 13:46:44.394731',2),(342,101.00,13781.600,'2025-11-08 13:46:44.436445',2),(343,102.00,13951.800,'2025-11-08 13:46:44.478115',2),(344,103.00,14121.800,'2025-11-08 13:46:44.561848',2),(345,104.00,14291.700,'2025-11-08 13:46:44.603411',2),(346,105.00,14461.400,'2025-11-08 13:46:44.645226',2),(347,106.00,14630.900,'2025-11-08 13:46:44.687149',2),(348,107.00,14800.200,'2025-11-08 13:46:44.728228',2),(349,108.00,14969.300,'2025-11-08 13:46:44.769900',2),(350,109.00,15138.000,'2025-11-08 13:46:44.836613',2),(351,110.00,15306.500,'2025-11-08 13:46:44.878324',2),(352,111.00,15474.700,'2025-11-08 13:46:44.920619',2),(353,112.00,15642.600,'2025-11-08 13:46:44.961665',2),(354,113.00,15810.100,'2025-11-08 13:46:45.020004',2),(355,114.00,15977.200,'2025-11-08 13:46:45.087114',2),(356,115.00,16144.000,'2025-11-08 13:46:45.128411',2),(357,116.00,16310.400,'2025-11-08 13:46:45.170154',2),(358,117.00,16476.300,'2025-11-08 13:46:45.228429',2),(359,118.00,16641.900,'2025-11-08 13:46:45.270088',2),(360,119.00,16806.900,'2025-11-08 13:46:45.312313',2),(361,120.00,16971.400,'2025-11-08 13:46:45.353536',2),(362,121.00,17135.500,'2025-11-08 13:46:45.394366',2),(363,122.00,17299.000,'2025-11-08 13:46:45.478607',2),(364,123.00,17462.000,'2025-11-08 13:46:45.520392',2),(365,124.00,17624.400,'2025-11-08 13:46:45.578681',2),(366,125.00,17786.100,'2025-11-08 13:46:45.620757',2),(367,126.00,17947.300,'2025-11-08 13:46:45.661921',2),(368,127.00,18107.900,'2025-11-08 13:46:45.704171',2),(369,128.00,18267.700,'2025-11-08 13:46:45.745342',2),(370,129.00,18426.900,'2025-11-08 13:46:45.786399',2),(371,130.00,18585.400,'2025-11-08 13:46:45.895064',2),(372,131.00,18743.100,'2025-11-08 13:46:45.937023',2),(373,132.00,18900.100,'2025-11-08 13:46:45.978780',2),(374,133.00,19056.300,'2025-11-08 13:46:46.033795',2),(375,134.00,19211.700,'2025-11-08 13:46:46.088984',2),(376,135.00,19366.200,'2025-11-08 13:46:46.147461',2),(377,136.00,19519.900,'2025-11-08 13:46:46.215380',2),(378,137.00,19672.700,'2025-11-08 13:46:46.376537',2),(379,138.00,19824.600,'2025-11-08 13:46:46.476493',2),(380,139.00,19975.600,'2025-11-08 13:46:46.559072',2),(381,140.00,20125.600,'2025-11-08 13:46:46.629793',2),(382,141.00,20274.600,'2025-11-08 13:46:46.792730',2),(383,142.00,20422.500,'2025-11-08 13:46:46.864801',2),(384,143.00,20569.500,'2025-11-08 13:46:46.957480',2),(385,144.00,20715.300,'2025-11-08 13:46:47.081322',2),(386,145.00,20860.000,'2025-11-08 13:46:47.148227',2),(387,146.00,21003.600,'2025-11-08 13:46:47.180452',2),(388,147.00,21146.000,'2025-11-08 13:46:47.214580',2),(389,148.00,21287.200,'2025-11-08 13:46:47.267524',2),(390,149.00,21427.100,'2025-11-08 13:46:47.309268',2),(391,150.00,21565.800,'2025-11-08 13:46:47.393069',2),(392,151.00,21703.100,'2025-11-08 13:46:47.474210',2),(393,152.00,21839.100,'2025-11-08 13:46:47.514763',2),(394,153.00,21973.700,'2025-11-08 13:46:47.557580',2),(395,154.00,22106.900,'2025-11-08 13:46:47.639431',2),(396,155.00,22238.600,'2025-11-08 13:46:47.682631',2),(397,156.00,22368.800,'2025-11-08 13:46:47.714853',2),(398,157.00,22497.500,'2025-11-08 13:46:47.743638',2),(399,158.00,22624.500,'2025-11-08 13:46:47.768660',2),(400,159.00,22749.900,'2025-11-08 13:46:47.839502',2),(401,160.00,22873.600,'2025-11-08 13:46:47.872916',2),(402,161.00,22995.600,'2025-11-08 13:46:47.948079',2),(403,162.00,23115.800,'2025-11-08 13:46:47.981772',2),(404,163.00,23234.100,'2025-11-08 13:46:48.026871',2),(405,164.00,23350.500,'2025-11-08 13:46:48.060202',2),(406,165.00,23465.000,'2025-11-08 13:46:48.086061',2),(407,166.00,23577.400,'2025-11-08 13:46:48.126982',2),(408,167.00,23687.700,'2025-11-08 13:46:48.160267',2),(409,168.00,23795.900,'2025-11-08 13:46:48.251112',2),(410,169.00,23901.800,'2025-11-08 13:46:48.314953',2),(411,170.00,24005.400,'2025-11-08 13:46:48.368772',2),(412,171.00,24106.600,'2025-11-08 13:46:48.423250',2),(413,172.00,24205.300,'2025-11-08 13:46:48.485754',2),(414,173.00,24301.400,'2025-11-08 13:46:48.510819',2),(415,174.00,24394.700,'2025-11-08 13:46:48.556060',2),(416,175.00,24485.300,'2025-11-08 13:46:48.589182',2),(417,176.00,24572.900,'2025-11-08 13:46:48.623263',2),(418,177.00,24657.400,'2025-11-08 13:46:48.673276',2),(419,178.00,24738.600,'2025-11-08 13:46:48.706592',2),(420,179.00,24816.500,'2025-11-08 13:46:48.764410',2),(421,180.00,24890.700,'2025-11-08 13:46:48.835740',2),(422,181.00,24961.000,'2025-11-08 13:46:48.925622',2),(423,182.00,25027.200,'2025-11-08 13:46:48.956720',2),(424,183.00,25088.900,'2025-11-08 13:46:49.006772',2),(425,184.00,25145.700,'2025-11-08 13:46:49.140184',2),(426,185.00,25197.200,'2025-11-08 13:46:49.194260',2),(427,186.00,25242.500,'2025-11-08 13:46:49.265239',2),(428,187.00,25280.700,'2025-11-08 13:46:49.325120',2),(429,188.00,25309.800,'2025-11-08 13:46:49.357223',2),(430,189.00,25323.900,'2025-11-08 13:46:49.427436',2),(431,5.00,137.000,'2025-11-08 14:05:23.068711',3),(432,10.00,388.000,'2025-11-08 14:05:23.108725',3),(433,15.00,712.000,'2025-11-08 14:05:23.170891',3),(434,20.00,1094.000,'2025-11-08 14:05:23.195903',3),(435,25.00,1524.000,'2025-11-08 14:05:23.229839',3),(436,30.00,1997.000,'2025-11-08 14:05:23.271799',3),(437,35.00,2506.000,'2025-11-08 14:05:23.296797',3),(438,40.00,3050.000,'2025-11-08 14:05:23.321829',3),(439,45.00,3623.000,'2025-11-08 14:05:23.367695',3),(440,50.00,4223.000,'2025-11-08 14:05:23.415227',3),(441,55.00,4847.000,'2025-11-08 14:05:23.480412',3),(442,60.00,5494.000,'2025-11-08 14:05:23.521632',3),(443,65.00,6161.000,'2025-11-08 14:05:23.546640',3),(444,70.00,6845.000,'2025-11-08 14:05:23.632253',3),(445,75.00,7546.000,'2025-11-08 14:05:23.689089',3),(446,80.00,8261.000,'2025-11-08 14:05:23.792618',3),(447,85.00,8989.000,'2025-11-08 14:05:23.909661',3),(448,90.00,9728.000,'2025-11-08 14:05:23.959662',3),(449,95.00,10477.000,'2025-11-08 14:05:23.992212',3),(450,100.00,11234.000,'2025-11-08 14:05:24.060107',3),(451,105.00,11998.000,'2025-11-08 14:05:24.109735',3),(452,110.00,12767.000,'2025-11-08 14:05:24.143084',3),(453,115.00,13541.000,'2025-11-08 14:05:24.187877',3),(454,120.00,14317.000,'2025-11-08 14:05:24.230642',3),(455,125.00,15094.000,'2025-11-08 14:05:24.280680',3),(456,130.00,15872.000,'2025-11-08 14:05:24.305229',3),(457,135.00,16648.000,'2025-11-08 14:05:24.330736',3),(458,140.00,17421.000,'2025-11-08 14:05:24.355346',3),(459,145.00,18191.000,'2025-11-08 14:05:24.401551',3),(460,150.00,18955.000,'2025-11-08 14:05:24.434847',3),(461,155.00,19712.000,'2025-11-08 14:05:24.468243',3),(462,160.00,20461.000,'2025-11-08 14:05:24.518241',3),(463,165.00,21200.000,'2025-11-08 14:05:24.551027',3),(464,170.00,21928.000,'2025-11-08 14:05:24.593914',3),(465,175.00,22643.000,'2025-11-08 14:05:24.676652',3),(466,180.00,23344.000,'2025-11-08 14:05:24.726718',3),(467,185.00,24028.000,'2025-11-08 14:05:24.796642',3),(468,190.00,24695.000,'2025-11-08 14:05:24.843368',3),(469,195.00,25341.000,'2025-11-08 14:05:24.876685',3),(470,200.00,25966.000,'2025-11-08 14:05:24.935247',3),(471,205.00,26566.000,'2025-11-08 14:05:24.997464',3),(472,210.00,27139.000,'2025-11-08 14:05:25.090342',3),(473,215.00,27682.000,'2025-11-08 14:05:25.145028',3),(474,220.00,28192.000,'2025-11-08 14:05:25.189146',3),(475,225.00,28665.000,'2025-11-08 14:05:25.230017',3),(476,230.00,29095.000,'2025-11-08 14:05:25.276890',3),(477,235.00,29477.000,'2025-11-08 14:05:25.326958',3),(478,240.00,29801.000,'2025-11-08 14:05:25.360280',3),(479,245.00,30052.000,'2025-11-08 14:05:25.393590',3),(480,250.00,30189.000,'2025-11-08 14:05:25.447587',3),(481,5.00,156.000,'2025-11-08 14:12:37.501719',4),(482,10.00,440.000,'2025-11-08 14:12:37.551908',4),(483,15.00,806.000,'2025-11-08 14:12:37.585024',4),(484,20.00,1236.000,'2025-11-08 14:12:37.648788',4),(485,25.00,1718.000,'2025-11-08 14:12:37.685953',4),(486,30.00,2247.000,'2025-11-08 14:12:37.745925',4),(487,35.00,2815.000,'2025-11-08 14:12:37.777691',4),(488,40.00,3419.000,'2025-11-08 14:12:37.811348',4),(489,45.00,4054.000,'2025-11-08 14:12:37.864956',4),(490,50.00,4717.000,'2025-11-08 14:12:37.905698',4),(491,55.00,5405.000,'2025-11-08 14:12:37.947584',4),(492,60.00,6115.000,'2025-11-08 14:12:37.994374',4),(493,65.00,6844.000,'2025-11-08 14:12:38.027779',4),(494,70.00,7592.000,'2025-11-08 14:12:38.064760',4),(495,75.00,8354.000,'2025-11-08 14:12:38.098097',4),(496,80.00,9130.000,'2025-11-08 14:12:38.131553',4),(497,85.00,9916.000,'2025-11-08 14:12:38.177828',4),(498,90.00,10712.000,'2025-11-08 14:12:38.211136',4),(499,95.00,11516.000,'2025-11-08 14:12:38.244454',4),(500,100.00,12325.000,'2025-11-08 14:12:38.277834',4),(501,105.00,13137.000,'2025-11-08 14:12:38.311129',4),(502,110.00,13952.000,'2025-11-08 14:12:38.344464',4),(503,115.00,14767.000,'2025-11-08 14:12:38.411324',4),(504,120.00,15581.000,'2025-11-08 14:12:38.546449',4),(505,125.00,16392.000,'2025-11-08 14:12:38.640862',4),(506,130.00,17198.000,'2025-11-08 14:12:38.749331',4),(507,135.00,17997.000,'2025-11-08 14:12:38.790417',4),(508,140.00,18788.000,'2025-11-08 14:12:38.832189',4),(509,145.00,19568.000,'2025-11-08 14:12:38.923809',4),(510,150.00,20336.000,'2025-11-08 14:12:38.969060',4),(511,155.00,21089.000,'2025-11-08 14:12:39.086845',4),(512,160.00,21826.000,'2025-11-08 14:12:39.145805',4),(513,165.00,22545.000,'2025-11-08 14:12:39.236551',4),(514,170.00,23242.000,'2025-11-08 14:12:39.297820',4),(515,175.00,23915.000,'2025-11-08 14:12:39.344805',4),(516,180.00,24562.000,'2025-11-08 14:12:39.391388',4),(517,185.00,25178.000,'2025-11-08 14:12:39.448848',4),(518,190.00,25761.000,'2025-11-08 14:12:39.521087',4),(519,195.00,26306.000,'2025-11-08 14:12:39.631098',4),(520,200.00,26808.000,'2025-11-08 14:12:39.681389',4),(521,205.00,27260.000,'2025-11-08 14:12:39.753522',4),(522,210.00,27653.000,'2025-11-08 14:12:39.887543',4),(523,215.00,27972.000,'2025-11-08 14:12:39.947390',4),(524,220.00,28191.000,'2025-11-08 14:12:40.003595',4),(525,222.00,28231.000,'2025-11-08 14:12:40.057551',4),(526,5.00,111.000,'2025-11-08 14:19:31.617547',5),(527,10.00,314.000,'2025-11-08 14:19:31.670174',5),(528,15.00,576.000,'2025-11-08 14:19:31.703326',5),(529,20.00,884.000,'2025-11-08 14:19:31.736671',5),(530,25.00,1229.000,'2025-11-08 14:19:31.770277',5),(531,30.00,1608.000,'2025-11-08 14:19:31.803393',5),(532,35.00,2016.000,'2025-11-08 14:19:31.854122',5),(533,40.00,2449.000,'2025-11-08 14:19:31.887588',5),(534,45.00,2904.000,'2025-11-08 14:19:31.920933',5),(535,50.00,3380.000,'2025-11-08 14:19:32.015862',5),(536,55.00,3874.000,'2025-11-08 14:19:32.108606',5),(537,60.00,4384.000,'2025-11-08 14:19:32.393935',5),(538,65.00,4908.000,'2025-11-08 14:19:32.450465',5),(539,70.00,5445.000,'2025-11-08 14:19:32.513824',5),(540,75.00,5992.000,'2025-11-08 14:19:32.575015',5),(541,80.00,6549.000,'2025-11-08 14:19:32.646696',5),(542,85.00,7114.000,'2025-11-08 14:19:32.674932',5),(543,90.00,7686.000,'2025-11-08 14:19:32.700401',5),(544,95.00,8262.000,'2025-11-08 14:19:32.754675',5),(545,100.00,8843.000,'2025-11-08 14:19:32.787937',5),(546,105.00,9426.000,'2025-11-08 14:19:32.821311',5),(547,110.00,10010.000,'2025-11-08 14:19:32.854640',5),(548,115.00,10595.000,'2025-11-08 14:19:32.900412',5),(549,120.00,11178.000,'2025-11-08 14:19:32.925369',5),(550,125.00,11758.000,'2025-11-08 14:19:33.000580',5),(551,130.00,12335.000,'2025-11-08 14:19:33.033170',5),(552,135.00,12906.000,'2025-11-08 14:19:33.063201',5),(553,140.00,13471.000,'2025-11-08 14:19:33.133598',5),(554,145.00,14028.000,'2025-11-08 14:19:33.158590',5),(555,150.00,14575.000,'2025-11-08 14:19:33.183866',5),(556,155.00,15112.000,'2025-11-08 14:19:33.208664',5),(557,160.00,15636.000,'2025-11-08 14:19:33.246530',5),(558,165.00,16146.000,'2025-11-08 14:19:33.308869',5),(559,170.00,16640.000,'2025-11-08 14:19:33.338199',5),(560,175.00,17116.000,'2025-11-08 14:19:33.441259',5),(561,180.00,17572.000,'2025-11-08 14:19:33.480817',5),(562,185.00,18005.000,'2025-11-08 14:19:33.546525',5),(563,190.00,18412.000,'2025-11-08 14:19:33.579918',5),(564,195.00,18791.000,'2025-11-08 14:19:33.624236',5),(565,200.00,19137.000,'2025-11-08 14:19:33.654983',5),(566,205.00,19444.000,'2025-11-08 14:19:33.688424',5),(567,210.00,19706.000,'2025-11-08 14:19:33.721700',5),(568,215.00,19909.000,'2025-11-08 14:19:33.771666',5),(569,220.00,20020.000,'2025-11-08 14:19:33.834584',5),(570,5.00,111.000,'2025-11-08 14:21:42.600268',6),(571,10.00,314.000,'2025-11-08 14:21:42.640007',6),(572,15.00,576.000,'2025-11-08 14:21:42.673994',6),(573,20.00,884.000,'2025-11-08 14:21:42.740047',6),(574,25.00,1229.000,'2025-11-08 14:21:42.790902',6),(575,30.00,1608.000,'2025-11-08 14:21:42.857478',6),(576,35.00,2016.000,'2025-11-08 14:21:42.890817',6),(577,40.00,2449.000,'2025-11-08 14:21:42.940100',6),(578,45.00,2904.000,'2025-11-08 14:21:42.973730',6),(579,50.00,3380.000,'2025-11-08 14:21:43.018918',6),(580,55.00,3874.000,'2025-11-08 14:21:43.049877',6),(581,60.00,4384.000,'2025-11-08 14:21:43.090908',6),(582,65.00,4908.000,'2025-11-08 14:21:43.124224',6),(583,70.00,5445.000,'2025-11-08 14:21:43.157586',6),(584,75.00,5992.000,'2025-11-08 14:21:43.222427',6),(585,80.00,6549.000,'2025-11-08 14:21:43.314123',6),(586,85.00,7114.000,'2025-11-08 14:21:43.463941',6),(587,90.00,7686.000,'2025-11-08 14:21:43.499657',6),(588,95.00,8262.000,'2025-11-08 14:21:43.533043',6),(589,100.00,8843.000,'2025-11-08 14:21:43.577507',6),(590,105.00,9426.000,'2025-11-08 14:21:43.607807',6),(591,110.00,10010.000,'2025-11-08 14:21:43.641132',6),(592,115.00,10595.000,'2025-11-08 14:21:43.685845',6),(593,120.00,11178.000,'2025-11-08 14:21:43.757820',6),(594,125.00,11758.000,'2025-11-08 14:21:43.791179',6),(595,130.00,12335.000,'2025-11-08 14:21:43.824497',6),(596,135.00,12906.000,'2025-11-08 14:21:43.869272',6),(597,140.00,13471.000,'2025-11-08 14:21:43.916247',6),(598,145.00,14028.000,'2025-11-08 14:21:43.949843',6),(599,150.00,14575.000,'2025-11-08 14:21:43.983178',6),(600,155.00,15112.000,'2025-11-08 14:21:44.018793',6),(601,160.00,15636.000,'2025-11-08 14:21:44.078398',6),(602,165.00,16146.000,'2025-11-08 14:21:44.108114',6),(603,170.00,16640.000,'2025-11-08 14:21:44.158023',6),(604,175.00,17116.000,'2025-11-08 14:21:44.191367',6),(605,180.00,17572.000,'2025-11-08 14:21:44.224683',6),(606,185.00,18005.000,'2025-11-08 14:21:44.258068',6),(607,190.00,18412.000,'2025-11-08 14:21:44.291411',6),(608,195.00,18791.000,'2025-11-08 14:21:44.336130',6),(609,200.00,19137.000,'2025-11-08 14:21:44.399799',6),(610,205.00,19444.000,'2025-11-08 14:21:44.444511',6),(611,210.00,19706.000,'2025-11-08 14:21:44.483190',6),(612,215.00,19909.000,'2025-11-08 14:21:44.516693',6),(613,220.00,20020.000,'2025-11-08 14:21:44.550035',6),(614,5.00,101.000,'2025-11-08 14:28:20.258996',7),(615,10.00,283.000,'2025-11-08 14:28:20.301512',7),(616,15.00,516.000,'2025-11-08 14:28:20.427045',7),(617,20.00,788.000,'2025-11-08 14:28:20.476645',7),(618,25.00,1091.000,'2025-11-08 14:28:20.509868',7),(619,30.00,1421.000,'2025-11-08 14:28:20.543299',7),(620,35.00,1772.000,'2025-11-08 14:28:20.576645',7),(621,40.00,2143.000,'2025-11-08 14:28:20.609957',7),(622,45.00,2529.000,'2025-11-08 14:28:20.643396',7),(623,50.00,2928.000,'2025-11-08 14:28:20.693392',7),(624,55.00,3337.000,'2025-11-08 14:28:20.726694',7),(625,60.00,3755.000,'2025-11-08 14:28:20.760079',7),(626,65.00,4179.000,'2025-11-08 14:28:20.798399',7),(627,70.00,4607.000,'2025-11-08 14:28:20.847740',7),(628,75.00,5036.000,'2025-11-08 14:28:20.913804',7),(629,80.00,5466.000,'2025-11-08 14:28:20.943478',7),(630,85.00,5894.000,'2025-11-08 14:28:20.988184',7),(631,90.00,6318.000,'2025-11-08 14:28:21.018422',7),(632,95.00,6736.000,'2025-11-08 14:28:21.051732',7),(633,100.00,7145.000,'2025-11-08 14:28:21.096522',7),(634,105.00,7544.000,'2025-11-08 14:28:21.126894',7),(635,110.00,7930.000,'2025-11-08 14:28:21.160233',7),(636,115.00,8300.000,'2025-11-08 14:28:21.204996',7),(637,120.00,8652.000,'2025-11-08 14:28:21.235237',7),(638,125.00,8982.000,'2025-11-08 14:28:21.268542',7),(639,130.00,9285.000,'2025-11-08 14:28:21.324799',7),(640,135.00,9557.000,'2025-11-08 14:28:21.351940',7),(641,140.00,9790.000,'2025-11-08 14:28:21.385262',7),(642,145.00,9972.000,'2025-11-08 14:28:21.418606',7),(643,150.00,10073.000,'2025-11-08 14:28:21.451957',7);
/*!40000 ALTER TABLE `barremage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `citerne`
--

DROP TABLE IF EXISTS `citerne`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `citerne` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code_citerne` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type_citerne` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `diametre_cm` decimal(8,2) DEFAULT NULL,
  `longueur_cm` decimal(8,2) DEFAULT NULL,
  `epaisseur_cm` decimal(8,2) DEFAULT NULL,
  `cod_art_fluide` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `libelle_fluide` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `actif` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_citerne` (`code_citerne`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `citerne`
--

LOCK TABLES `citerne` WRITE;
/*!40000 ALTER TABLE `citerne` DISABLE KEYS */;
INSERT INTO `citerne` VALUES (1,'STC2','Citerne 2 Station Service','sous_sol',NULL,NULL,NULL,'243000102W','GASOIL ORDINAIRE                                  ',1,'2025-11-08 10:38:03.099795','2025-11-08 15:46:23.856333'),(2,'STCSS','Citerne Gasoil SS Station Service','sur_skid',NULL,NULL,NULL,'243000312Z','GASOIL SANS SOUFRE                                ',1,'2025-11-08 13:33:50.225290','2025-11-08 15:46:38.892269'),(3,'PGC1','Citerne 1 Parc Gasoil','sur_skid',NULL,NULL,NULL,'243000102W','GASOIL ORDINAIRE                                  ',1,'2025-11-08 13:54:07.125901','2025-11-08 15:45:23.026382'),(4,'PGC2','Citerne 2 Parc Gasoil','sur_skid',NULL,NULL,NULL,'243000102W','GASOIL ORDINAIRE                                  ',1,'2025-11-08 14:08:16.709343','2025-11-08 15:45:50.982226'),(5,'PGC3','Citerne 3 Parc Gasoil','sur_skid',NULL,NULL,NULL,'243000102W','GASOIL ORDINAIRE                                  ',1,'2025-11-08 14:14:09.691440','2025-11-08 15:46:00.888193'),(6,'PGC4','Citerne 4 Parc Gasoil','sur_skid',NULL,NULL,NULL,'243000102W','GASOIL ORDINAIRE                                  ',1,'2025-11-08 14:18:39.208451','2025-11-08 15:46:16.239401'),(7,'TranspC','Citerne 10000 Transport','sur_skid',NULL,NULL,NULL,NULL,NULL,1,'2025-11-08 14:26:04.021077','2025-11-08 14:26:04.021098');
/*!40000 ALTER TABLE `citerne` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consommation_carburant`
--

DROP TABLE IF EXISTS `consommation_carburant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consommation_carburant` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date_ravitaillement` date NOT NULL,
  `volume_l` decimal(8,2) NOT NULL,
  `type_carburant` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `observation` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `engin_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `consommation_carburant_engin_id_ba9974d3_fk_engin_id` (`engin_id`),
  CONSTRAINT `consommation_carburant_engin_id_ba9974d3_fk_engin_id` FOREIGN KEY (`engin_id`) REFERENCES `engin` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consommation_carburant`
--

LOCK TABLES `consommation_carburant` WRITE;
/*!40000 ALTER TABLE `consommation_carburant` DISABLE KEYS */;
/*!40000 ALTER TABLE `consommation_carburant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_articlecaracteristique`
--

DROP TABLE IF EXISTS `core_articlecaracteristique`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_articlecaracteristique` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `cod_art` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `valeur` longtext COLLATE utf8mb4_unicode_ci,
  `caracteristique_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_articlecaracteristi_cod_art_caracteristique__9b2e0002_uniq` (`cod_art`,`caracteristique_id`),
  KEY `core_articlecaracter_caracteristique_id_5e81bbf9_fk_core_cara` (`caracteristique_id`),
  CONSTRAINT `core_articlecaracter_caracteristique_id_5e81bbf9_fk_core_cara` FOREIGN KEY (`caracteristique_id`) REFERENCES `core_caracteristique` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_articlecaracteristique`
--

LOCK TABLES `core_articlecaracteristique` WRITE;
/*!40000 ALTER TABLE `core_articlecaracteristique` DISABLE KEYS */;
INSERT INTO `core_articlecaracteristique` VALUES (2,'000000000A','10',71),(3,'581200078Q','10',99),(5,'000000000A','10',40),(6,'416720490E','oui',129),(7,'774000001Z','165/70/14',1),(8,'000000000A','10',22),(9,'000000000A','11',52),(10,'243000102W','20000',131),(11,'243000312Z','8000',131);
/*!40000 ALTER TABLE `core_articlecaracteristique` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_articlefamily`
--

DROP TABLE IF EXISTS `core_articlefamily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_articlefamily` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci,
  `parent_id` bigint DEFAULT NULL,
  `code_segment` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_code` varchar(9) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_articlefamily_parent_id_24479077_fk_core_articlefamily_id` (`parent_id`),
  KEY `core_articlefamily_full_code_d0c82f32` (`full_code`),
  CONSTRAINT `core_articlefamily_parent_id_24479077_fk_core_articlefamily_id` FOREIGN KEY (`parent_id`) REFERENCES `core_articlefamily` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=154 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_articlefamily`
--

LOCK TABLES `core_articlefamily` WRITE;
/*!40000 ALTER TABLE `core_articlefamily` DISABLE KEYS */;
INSERT INTO `core_articlefamily` VALUES (6,'Engrais Naturels et minereaux non metallurgiques engrais brute','Matieres et Produits Chimiques',NULL,'207','207'),(7,'Engrais naturels brute','',6,'1','2071'),(8,'Guano et autre engrais non élabores chimiquement','',7,'1','20711'),(9,'Nitrate de soduim naturel','',7,'2','20712'),(10,'Phosphate naturels, apahtes et argiles naturelle','',7,'3','20713'),(11,'Sels de potassium naturels bruts','',7,'4','20714'),(12,'Minerais Mitalliferes et dechets de metaux; Minerais de fer et concentres','Matieres et Produits Chimiques',NULL,'208','208'),(13,'Fibres vegetales autres que le coton et le jute','Matieres et Produits Chimiques',NULL,'215','215'),(14,'Accessoires d\'habillement et articles textiles usages, chiffons et similaires','Matieres et Produits Chimiques',NULL,'217','217'),(15,'Vaseline et Cires Minerales','Matieres et Produits Chimiques',NULL,'236','236'),(16,'Petrole Brute ou semi-raffine','Matieres et Produits Chimiques',NULL,'240','240'),(17,'Carburants pour moteurs (Ethers de petrole et essence)','Matieres et Produits Chimiques',NULL,'241','241'),(18,'Petrole d\'eclairage ou kerosene et white sprit','Matieres et Produits Chimiques',NULL,'242','242'),(19,'Huiles distillees legeres (Gasoil et combustibles distilles legers)','Matieres et Produits Chimiques',NULL,'243','243'),(20,'Huile et graisses lubrifiantes ayant une proportion d\'huiles de petrole egale ou superieure à 70% en poids','Matieres et Produits Chimiques',NULL,'245','245'),(21,'Huiles et Graisses Lubrifiantes ayant une proportion d\'huiles de petrole inferieure à 70% en poids','Matieres et Produits Chimiques',NULL,'246','246'),(22,'Brai, Resine, Asphalte de petrole et huiles non lubrifiantes','Matieres et Produits Chimiquesر',NULL,'247','247'),(23,'Hydrocarbures Gazeux et gaz de procedes','Matieres et Produits Chimiques',NULL,'248','248'),(24,'Produits Chimiques Organiques','Matieres et Produits Chimiques',NULL,'261','261'),(25,'Produits Chimiques Inorganiques ( à l\'exception de ceux prevus dans la classe 263)','Matieres et Produits Chimiques',NULL,'262','262'),(26,'Autres Produits Inorganiques : Sels et perseles metalliques des acides inorganiques','Matieres et Produits Chimiques',NULL,'263','263'),(27,'Produits Chimiques medicinaux et pharmaceutiques','Matieres et Produits Chimiques',NULL,'266','266'),(28,'Savons, Produits detersifs et produits d\'entretient','Matieres et Produits Chimiques',NULL,'268','268'),(29,'Pigments, Peintures, Vernis','Matieres et Produits Chimiques',NULL,'273','273'),(30,'Engrais Manufactures','',NULL,'275','275'),(31,'Matieres Plastiques et resines artificielles','',NULL,'276','276'),(32,'Autres Matieres et Produits Chimiques','Matieres et Produits Chimiques',NULL,'279','279'),(33,'Fils et Barres etires, en fer ou en acier, de section transversable plein, de forme et de dimension quelconque','Fils et Barres etires, en fer ou en acier, de section transversable plein, de forme et de dimension quelconque',NULL,'305','305'),(34,'Eangrais naturels et Minereaux bruts non metallurgiques (Pierres - Sables - Gravier - Travetins - Granit - Porphyre - Pierres à chaux et ciment)','',6,'3','2073'),(36,'Ardoise Brute','Pierres de tailles et ddee contruction brute et de grossies',34,'110','2073110'),(37,'Marbres et pierres calcaires de taille et de construction','',34,'120','2073120'),(38,'Granits, prophyres, basaltes etc…','',34,'130','2073130'),(39,'Gypses, platres, colores','',34,'210','2073210'),(40,'Pierres à chaud ou ciment et autres castines','',34,'220','2073220'),(41,'Sables, sauf les sables métalliféres','',34,'300','2073300'),(42,'Gravier, pierres concassées, compris macadam et tarmacadam','',34,'400','2073400'),(43,'Autres Mineraux Bruts (Nature des Mineraux)','',6,'6','2076'),(44,'Asphalts et bitumes naturels','',43,'100','2076100'),(45,'Abresifs naturels terres d\'infusoires Emeri pulverise corindon naturel diamants indstriels','',6,'5','2075'),(46,'Diaments industriels','',45,'100','2075100'),(47,'Poudres de pierres mi-prés, nature ou synthé','',45,'210','2075210'),(48,'Terres d\'infusoires, Farines silic. Et fossiles','',45,'220','2075220'),(49,'Pierre ponce, émeri et corindon','',45,'230','2075230'),(50,'Argiles et autres mineraux réfractaires simil.','',43,'210','2076210'),(51,'Graphite naturel','',43,'220','2076220'),(52,'Dolomie','',43,'230','2076230'),(53,'Magnésite','',43,'240','2076240'),(54,'Sel gemme, fin, marin, etc…','',43,'300','2076300'),(55,'Amiante','',43,'400','2076400'),(56,'Quartz naturel et quartzite','',43,'510','2076510'),(57,'Mica','',43,'520','2076520'),(58,'Cryolithe et chialithe naturelles','',43,'530','2076530'),(59,'Feldspath, spath fluor, Leucite','',43,'540','2076540'),(60,'Scories, laitiers, dechets de la fabr de fer','',43,'610','2076610'),(61,'Autres scories et cendres y compris les cendres de varech','',43,'620','2076620'),(62,'Craies','',43,'910','2076910'),(63,'Terres Colorantes','',43,'920','2076920'),(64,'Sulfate et carbonate de baryum naturel','',43,'930','2076930'),(65,'Erume de mer naturelle, ambre et jais','',43,'940','2076940'),(66,'Stéatite naturelle, tale','',43,'950','2076950'),(67,'Sulfures d\'arsenic naturels','',43,'960','2076960'),(68,'Borates naturels bruts','',43,'970','2076970'),(69,'Autres matieres minérales','',43,'990','2076990'),(70,'Minerais de fer et concentres','',12,'1','2081'),(71,'Minerais de fer et concentrés (à vexelusion des pyrites de fer grillées)','Nature du minerai',70,'3','20813'),(72,'Pyrites de fer grillées','Nature du minerai',70,'4','20814'),(73,'Lin brut et traité, déchets et étoupe','',13,'1','2151'),(74,'Chanvre brut et traité, dechets étoupe','',13,'2','2152'),(75,'Rami brute, déchets et étoupe','',13,'3','2153'),(76,'Sisal et autres fibres de la famille de agaves: leurs déchets','',13,'4','2154'),(77,'Chanvre de manille, dechets et étoupe','',13,'5','2155'),(78,'Autres fibres textiles végétales et leurs déchets','',13,'8','2158'),(79,'Ruban de fibre filtrante','',74,'000','2152000'),(80,'Autres articles en chanvre taités','',74,'009','2152009'),(81,'Sac','',78,'006','2158006'),(82,'Articles d\'habillement usagés, en matieres textiles','Acc. d\'habillement et textilles usages, chifffons et similaire',14,'01','21701'),(83,'Chiffons, ficelles, cordes ou articles similaires hors d\'usage','Acc. d\'habillement et textilles usages, chifffons et similaire',14,'02','21702'),(84,'Vaslines','',15,'1','2361'),(85,'Cires minérales','',15,'2','2362'),(86,'Nature du produit: huile brurtes de petrole','',16,'01','24001'),(87,'Nature du produit: petrole semi-raffine','',16,'02','24002'),(88,'Algériens','',16,'0X0','2400X0'),(89,'Orientaux','',16,'0X4','2400X4'),(90,'Russes','',16,'0X9','2400X9'),(91,'de 10 à 10,9','',16,'0XX10','2400XX10'),(92,'de 11 à 11,9','',16,'0XX11','2400XX11'),(93,'de 12 à 12,9','',16,'0XX12','2400XX12'),(94,'de 13 à 13,9','',16,'0XX13','2400XX13'),(95,'de 14 à 14,9','',16,'0XX14','2400XX14'),(96,'de 15 à 15,9','',16,'0XX15','2400XX15'),(97,'de 16 à 16,9','',16,'0XX16','2400XX16'),(98,'de 17 à 17,9','',16,'0XX17','2400XX17'),(99,'de 18 à 18,9','',16,'0XX18','2400XX18'),(100,'de 19 à 19,9','',16,'0XX19','2400XX19'),(101,'de 20 à 20,9','',16,'0XX20','2400XX20'),(102,'de 21 à 21,9','',16,'0XX21','2400XX21'),(103,'de 22 à 22,9','',16,'0XX22','2400XX22'),(104,'de 23 à 23,9','',16,'0XX23','2400XX23'),(105,'de 24 à 24,9','',16,'0XX24','2400XX24'),(106,'de 25 à 25,9','',16,'0XX25','2400XX25'),(107,'de 26 à 26,9','',16,'0XX26','2400XX26'),(108,'de 27 à 27,9','',16,'0XX27','2400XX27'),(109,'de 28 à 28,9','',16,'0XX28','2400XX28'),(110,'de 29 à 29,9','',16,'0XX29','2400XX29'),(111,'de 30 à 30,9','',16,'0XX30','2400XX30'),(112,'de 31 à 31,9','',16,'0XX31','2400XX31'),(113,'de 32 à 32,9','',16,'0XX32','2400XX32'),(114,'de 33 à 33,9','',16,'0XX33','2400XX33'),(115,'de 34 à 34,9','',16,'0XX34','2400XX34'),(116,'de 35 à 35,9','',16,'0XX35','2400XX35'),(117,'de 36 à 36,9','',16,'0XX36','2400XX36'),(118,'de 37 à 37,9','',16,'0XX37','2400XX37'),(119,'de 38 à 38,9','',16,'0XX38','2400XX38'),(120,'de 39 à 39,9','',16,'0XX39','2400XX39'),(121,'de 40 à 40,9','',16,'0XX40','2400XX40'),(122,'de 41 à 41,9','',16,'0XX41','2400XX41'),(123,'de 42 à 42,9','',16,'0XX42','2400XX42'),(124,'de 43 à 43,9','',16,'0XX43','2400XX43'),(125,'de 44 à 44,9','',16,'0XX44','2400XX44'),(126,'de 45 à 45,9','',16,'0XX45','2400XX45'),(127,'Petrole Brute ou semi-raffine','',16,'0','2400'),(128,'Position Douaniere Etrangére','Position Douaniere Etrangére Nationalisée Nationalisée',127,'XXXX0','2400XXXX0'),(129,'Position Douaniere Nationalisée','',127,'XXXX2','2400XXXX2'),(130,'Position Douaniere Zone Franche','',127,'XXXX3','2400XXXX3'),(131,'Carburants pour moteurs (Ethers de petrole et essence)','',17,'000','241000'),(132,'Position Douaniere Nationalisée','',131,'XX2','241000XX2'),(133,'Petrole d\'eclairage ou kerosene et white sprit','',18,'000','242000'),(134,'Position Douaniere Nationalisée','',133,'XX2','242000XX2'),(135,'Huiles distillees legeres (Gasoil et combustibles distilles legers)','',19,'000','243000'),(136,'Position Douaniere Nationalisée','',135,'XX2','243000XX2'),(137,'Huile et graisses lubrifiantes ayant une proportion d\'huiles de petrole egale ou superieure à 70% en poids','',20,'0','2450'),(138,'Producteur AGIP | Wolf','',137,'1','24501'),(139,'Producteur AUDCO | BP','XX 00-->49 AUDCO\r\nXX 50-->99 BP',137,'2','24502'),(140,'Producteur BELLEVILLE | ELF','XX 00-->49 BELLEVILLE \r\nXX 50-->99 ELF',137,'3','24503'),(141,'Producteur JET LUBE | LOCKHEED','',137,'4','24504'),(142,'Producteur MOBIL','',137,'5','24505'),(143,'Producteur ESSO','',137,'6','24506'),(144,'Producteur ROCKWELL | SNDP','',137,'7','24507'),(145,'Fut (Cylindre)','',139,'XX1','24502XX1'),(146,'Bidon (18 KG)','',139,'XX4','24502XX4'),(147,'Autres Condittionnements','',139,'XX9','24502XX9'),(148,'Position Douaniere Autres  usages','',137,'XXXX9','2450XXXX9'),(149,'Position Douaniere Pour Robinetterie','',140,'XXX5','24503XXX5'),(150,'Récipient (20 lt)','',140,'XX4','24503XX4'),(151,'En Calibre (Bougie)','',140,'XX7','24503XX7'),(152,'Autres Condittionnements','',140,'XX9','24503XX9'),(153,'Position Douaniere Autres  usages','',140,'XXX9','24503XXX9');
/*!40000 ALTER TABLE `core_articlefamily` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_articleimage`
--

DROP TABLE IF EXISTS `core_articleimage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_articleimage` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `cod_art` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `image` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_articleimage`
--

LOCK TABLES `core_articleimage` WRITE;
/*!40000 ALTER TABLE `core_articleimage` DISABLE KEYS */;
INSERT INTO `core_articleimage` VALUES (18,'000000000A','articles/000000000A/téléchargement.jpeg','2025-09-14 08:01:19.446084');
/*!40000 ALTER TABLE `core_articleimage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_caracteristique`
--

DROP TABLE IF EXISTS `core_caracteristique`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_caracteristique` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type_valeur` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `unite` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `utilisable_dans_recherche` tinyint(1) NOT NULL,
  `parent_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `core_caracteristique_parent_id_e307f882_fk_core_cara` (`parent_id`),
  CONSTRAINT `core_caracteristique_parent_id_e307f882_fk_core_cara` FOREIGN KEY (`parent_id`) REFERENCES `core_caracteristique` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=132 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_caracteristique`
--

LOCK TABLES `core_caracteristique` WRITE;
/*!40000 ALTER TABLE `core_caracteristique` DISABLE KEYS */;
INSERT INTO `core_caracteristique` VALUES (1,'Dimensions & Forme','text','',1,NULL),(2,'Matière & Composition','text','',1,NULL),(3,'Pression & Température','text','',1,NULL),(4,'Électrique','text','',1,NULL),(5,'Mécanique','text','',1,NULL),(6,'Hydraulique & Pneumatique','text','',1,NULL),(7,'Connectique & Raccordement','text',NULL,1,NULL),(8,'Identification & Traçabilité','text','',1,NULL),(9,'Performance & Durée','text','',1,NULL),(10,'Sécurité','text','',1,NULL),(11,'Environnement','text','',1,NULL),(12,'Outillage & Maintenance','text','',1,NULL),(13,'Spécifique à l\'application','text','',1,NULL),(14,'Diamètre nominal','unit','mm',1,1),(15,'Diamètre extérieur','unit','mm',1,1),(16,'Diamètre intérieur','unit','mm',1,1),(17,'Épaisseur de paroi','unit','mm',1,1),(18,'Longueur','unit','m',1,1),(19,'Largeur','unit','mm',1,1),(20,'Hauteur','unit','mm',1,1),(21,'Poids','unit','kg',1,1),(22,'Volume','unit','m³',1,1),(23,'Section','unit','cm²',1,1),(24,'Rayon de courbure','unit','mm',1,1),(25,'Matériau principal','choice','',1,2),(26,'Revêtement','text','',1,2),(27,'Densité','unit','g/cm³',1,2),(28,'Résistance à la traction','unit','MPa',1,2),(29,'Limite élastique','unit','MPa',1,2),(30,'Type de plastique','choice','',1,2),(31,'Teneur en carbone','number','%',1,2),(32,'Dureté (Rockwell)','number','',1,2),(33,'Pression nominale','unit','bar',1,3),(34,'Pression max','unit','bar',1,3),(35,'Pression min','unit','bar',1,3),(36,'Température nominale','unit','°C',1,3),(37,'Température max','unit','°C',1,3),(38,'Température min','unit','°C',1,3),(39,'Température de fonctionnement','text','°C',1,3),(40,'Classe de pression','text','PN',1,3),(41,'Pression nominale','unit','bar',1,3),(42,'Pression max','unit','bar',1,3),(43,'Pression min','unit','bar',1,3),(44,'Température nominale','unit','°C',1,3),(45,'Température max','unit','°C',1,3),(46,'Température min','unit','°C',1,3),(47,'Température de fonctionnement','text','°C',1,3),(48,'Classe de pression','text','PN',1,3),(49,'Tension nominale','unit','V',1,4),(50,'Tension d\'isolation','unit','V',1,4),(51,'Intensité nominale','unit','A',1,4),(52,'Puissance électrique','unit','kW',1,4),(53,'Puissance hydraulique','unit','HP',1,4),(54,'Fréquence','unit','Hz',1,4),(55,'Facteur de puissance','number','',1,4),(56,'Degré de protection','text','IP',1,4),(57,'Type de courant','choice','',1,4),(58,'Nombre de pôles','number','',1,4),(59,'Capacité de démarrage','unit','kVA',1,4),(60,'Vitesse nominale','unit','tr/min',1,5),(61,'Vitesse max','unit','tr/min',1,5),(62,'Couple nominal','unit','Nm',1,5),(63,'Type de transmission','choice','',1,5),(64,'Type de joint','choice','',1,5),(65,'Type de filetage','text','',1,5),(66,'Pas de filetage','unit','mm',1,5),(67,'Diamètre de filetage','unit','mm',1,5),(68,'Type de roulement','text','',1,5),(69,'Jeu mécanique','unit','mm',1,5),(70,'Débit nominal','unit','l/min',1,6),(71,'Débit max','unit','l/min',1,6),(72,'Pression hydraulique','unit','bar',1,6),(73,'Type de fluide','choice','',1,6),(74,'Viscosité','unit','cSt',1,6),(75,'Filtre intégré','boolean','',1,6),(76,'Type de raccord','choice','',1,7),(77,'Norme des raccordement','text',NULL,1,7),(78,'Nombre de voies','number',NULL,1,7),(79,'Type de prise','text','',1,7),(80,'Type de fiche','text','',1,7),(81,'Section du câble','unit','mm²',1,7),(82,'Type de connecteur','text','',1,7),(83,'Type de raccord','choice','',1,7),(84,'Norme de raccordement','text','',1,7),(85,'Nombre des voies','number',NULL,1,NULL),(86,'Type de prise','text','',1,7),(87,'Type de fiche','text','',1,7),(88,'Section du câble','unit','mm²',1,7),(89,'Type de connecteur','text','',1,7),(90,'Rendement','number','%',1,9),(91,'Durée de vie','unit','heures',1,9),(92,'Durée de garantie','unit','mois',1,9),(93,'Précision','number','%',1,9),(94,'Fréquence de maintenance','unit','heures',1,9),(95,'Cycle de vie','number','',1,9),(96,'Charge maximale','unit','t',1,10),(97,'Charge de rupture','unit','t',1,10),(98,'Norme de sécurité','text','',1,10),(99,'Classe de risque','choice','',1,10),(100,'Certification','text','',1,10),(101,'Protection contre les surtensions','boolean','',1,10),(102,'Température ambiante','text','°C',1,11),(103,'Humidité relative max','number','%',1,11),(104,'Résistance aux UV','boolean','',1,11),(105,'Indice de protection','text','IP',1,11),(106,'Résistance aux chocs','text','IK',1,11),(107,'Outil de montage','text','',1,12),(108,'Outil de démontage','text','',1,12),(109,'Couple de serrage','unit','Nm',1,12),(110,'Type de clé','text','',1,12),(111,'Lubrifiant recommandé','text','',1,12),(112,'Fréquence de graissage','unit','heures',1,12),(113,'Application','choice','',1,13),(114,'Type d\'appareil','text','',1,13),(115,'Classe de forage','text','',1,13),(116,'Type de turbine','choice','',1,13),(117,'Type de vanne','choice','',1,13),(118,'Type de pompe','choice','',1,13),(119,'Type de moteur','choice','',1,13),(120,'Type de filtre','choice','',1,13),(121,'Shedule','choice','',1,13),(122,'Norme (API, ASME, DIN)','text','',1,13),(123,'Vanne papillon','text','',0,117),(124,'Vanne bille','text','',0,117),(125,'Vanne à guillotine','text','',0,117),(126,'Forage','text','',0,113),(127,'Turbine à gaz','text','',0,113),(128,'Laboratoire','text','',0,113),(129,'Identifié par numéro de série','boolean',NULL,1,NULL),(130,'Has a Serial Number','boolean',NULL,1,NULL),(131,'Has Stock security','boolean',NULL,1,NULL);
/*!40000 ALTER TABLE `core_caracteristique` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_companyinfo`
--

DROP TABLE IF EXISTS `core_companyinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_companyinfo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address` longtext COLLATE utf8mb4_unicode_ci,
  `phone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `logo` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_companyinfo`
--

LOCK TABLES `core_companyinfo` WRITE;
/*!40000 ALTER TABLE `core_companyinfo` DISABLE KEYS */;
INSERT INTO `core_companyinfo` VALUES (1,'شركة البترول الوطنية','شارع النفط، الجزائر العاصمة','+213 21 123 456','contact@nationalpetro.dz','','2025-08-14 09:40:25.581394','2025-08-14 09:40:25.581491');
/*!40000 ALTER TABLE `core_companyinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_page`
--

DROP TABLE IF EXISTS `core_page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_page` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name_fr` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name_ar` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `url_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order` int NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url_name` (`url_name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_page`
--

LOCK TABLES `core_page` WRITE;
/*!40000 ALTER TABLE `core_page` DISABLE KEYS */;
INSERT INTO `core_page` VALUES (1,'Tableau de bord','لوحة القيادة','dashboard',1,1,'2025-08-14 09:40:25.643456','2025-08-14 09:40:25.643525'),(2,'Gestion des Utilisateurs','إدارة المستخدمين','users',2,1,'2025-08-14 09:40:25.693933','2025-08-14 09:40:25.693999'),(3,'Rapports','التقارير','reports',3,1,'2025-08-14 09:40:25.742087','2025-08-14 09:40:25.742160'),(4,'Maintenance','الصيانة','maintenance',4,1,'2025-08-14 09:40:25.792012','2025-08-14 09:40:25.792051'),(5,'Paramètres','الإعدادات','settings',5,1,'2025-08-14 09:40:25.835250','2025-08-14 09:40:25.835317'),(6,'Gestion des Articles','إدارة السلع','articles',4,1,'2025-09-03 16:10:02.252491','2025-09-03 16:10:02.252532'),(7,'Gestion des Caractéristiques Articles','إدارة خصائص السلع','article_caracteristiques',10,1,'2025-09-03 16:10:02.252491','2025-09-03 16:10:02.252491');
/*!40000 ALTER TABLE `core_page` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_permissionmatrix`
--

DROP TABLE IF EXISTS `core_permissionmatrix`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_permissionmatrix` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `can_consulte` tinyint(1) NOT NULL,
  `can_insert` tinyint(1) NOT NULL,
  `can_update` tinyint(1) NOT NULL,
  `can_delete` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `page_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_permissionmatrix_user_id_page_id_0e7b8575_uniq` (`user_id`,`page_id`),
  KEY `core_permissionmatrix_page_id_0393404f_fk_core_page_id` (`page_id`),
  CONSTRAINT `core_permissionmatrix_page_id_0393404f_fk_core_page_id` FOREIGN KEY (`page_id`) REFERENCES `core_page` (`id`),
  CONSTRAINT `core_permissionmatrix_user_id_b17df8cc_fk_accounts_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_permissionmatrix`
--

LOCK TABLES `core_permissionmatrix` WRITE;
/*!40000 ALTER TABLE `core_permissionmatrix` DISABLE KEYS */;
INSERT INTO `core_permissionmatrix` VALUES (1,1,1,1,1,'2025-08-14 09:40:45.611419','2025-08-16 09:18:43.443654',1,1),(2,1,1,1,1,'2025-08-14 09:40:45.661308','2025-08-16 09:19:52.621643',2,1),(3,1,1,1,1,'2025-08-14 09:40:45.752065','2025-08-14 09:40:45.752134',3,1),(4,1,1,1,1,'2025-08-14 09:40:45.802651','2025-08-14 09:40:45.802719',4,1),(6,1,1,1,1,'2025-08-16 09:20:04.892040','2025-08-16 09:20:04.892059',5,1),(7,1,1,1,1,'2025-09-03 16:13:41.482510','2025-09-03 16:14:27.846901',6,1),(8,1,1,1,1,'2025-09-11 10:35:38.307733','2025-09-12 06:32:59.205744',7,1),(9,1,1,1,1,'2025-11-07 16:13:39.248218','2025-11-07 16:13:39.248237',1,3),(10,1,1,1,1,'2025-11-07 16:13:51.131648','2025-11-07 16:13:51.131669',2,3),(11,1,1,1,1,'2025-11-07 16:13:56.680440','2025-11-07 16:13:56.680457',3,3),(12,1,1,1,1,'2025-11-07 16:14:00.575878','2025-11-07 16:14:00.575900',4,3),(13,1,1,1,1,'2025-11-07 16:14:05.630726','2025-11-07 16:14:05.630744',6,3),(14,1,1,1,1,'2025-11-07 16:14:09.686745','2025-11-07 16:14:09.686762',5,3),(15,1,1,1,1,'2025-11-07 16:14:12.870216','2025-11-07 16:14:12.870235',7,3);
/*!40000 ALTER TABLE `core_permissionmatrix` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_piecejointeetape`
--

DROP TABLE IF EXISTS `core_piecejointeetape`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_piecejointeetape` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fichier` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom_original` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_upload` datetime(6) NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `etape_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_piecejointeetape_etape_id_9cafb485_fk_suivi_dossier_id` (`etape_id`),
  CONSTRAINT `core_piecejointeetape_etape_id_9cafb485_fk_suivi_dossier_id` FOREIGN KEY (`etape_id`) REFERENCES `suivi_dossier` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_piecejointeetape`
--

LOCK TABLES `core_piecejointeetape` WRITE;
/*!40000 ALTER TABLE `core_piecejointeetape` DISABLE KEYS */;
INSERT INTO `core_piecejointeetape` VALUES (1,'etapes/0176/2025L/contrat_13-2024_Ambulance.pdf','contrat 13-2024 Ambulance.pdf','2025-10-31 10:45:38.702343','',101),(2,'etapes/0176/2025L/25667546-95ed-43d9-a1a2-731c9caa3167_img09571.tif','25667546-95ed-43d9-a1a2-731c9caa3167_img09571.tif','2025-10-31 10:45:52.207124','',101),(3,'etapes/0176/2025L/DR_AIR_LIQUIDE_25051_4.tif','DR AIR LIQUIDE 25051 (4).tif','2025-10-31 14:59:15.655617','',101),(4,'etapes/0176/2025L/BP_MAGASIN_CHZN_bW8hhfq.xlsx','BP MAGASIN CH+ZN.xlsx','2025-11-01 06:42:53.790586','Pièce jointe de l\'email',106),(5,'etapes/0176/2025L/BP_MAGASIN_CHZN_iat8Nhs.xlsx','BP MAGASIN CH+ZN.xlsx','2025-11-01 06:42:53.859597','Pièce jointe de l\'email',106),(6,'etapes/0176/2025L/BP_MAGASIN_CHZN_jzAxeei.xlsx','BP MAGASIN CH+ZN.xlsx','2025-11-01 06:43:29.159583','',105),(9,'etapes/0176/2025L/check_list_table.docx','check_list_table.docx','2025-11-01 06:56:13.134580','Pièce jointe de l\'email',106),(10,'etapes/0176/2025L/check_list_table_NRgYThG.docx','check_list_table.docx','2025-11-01 06:56:13.184068','Pièce jointe de l\'email',106);
/*!40000 ALTER TABLE `core_piecejointeetape` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_serialunit`
--

DROP TABLE IF EXISTS `core_serialunit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_serialunit` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `cod_art` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `val_art` int NOT NULL,
  `numero_serie` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_ajout` datetime(6) NOT NULL,
  `statut` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `emplacement` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `utilisateur` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_serialunit_cod_art_val_art_numero_serie_2dd9fdaa_uniq` (`cod_art`,`val_art`,`numero_serie`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_serialunit`
--

LOCK TABLES `core_serialunit` WRITE;
/*!40000 ALTER TABLE `core_serialunit` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_serialunit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detail_avis`
--

DROP TABLE IF EXISTS `detail_avis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detail_avis` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `item` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cod_art` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `lib_art` longtext COLLATE utf8mb4_unicode_ci,
  `qte_commande` decimal(15,3) DEFAULT NULL,
  `qte_receptionnee` decimal(15,3) NOT NULL,
  `um_commande` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `um_reception` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observation` longtext COLLATE utf8mb4_unicode_ci,
  `avis_id` bigint NOT NULL,
  `conformite` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `detail_avis_avis_id_5d0365_idx` (`avis_id`,`item`),
  KEY `detail_avis_cod_art_da8ca9_idx` (`cod_art`),
  CONSTRAINT `detail_avis_avis_id_72ad7a7b_fk_avis_arrivee_id` FOREIGN KEY (`avis_id`) REFERENCES `avis_arrivee` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detail_avis`
--

LOCK TABLES `detail_avis` WRITE;
/*!40000 ALTER TABLE `detail_avis` DISABLE KEYS */;
INSERT INTO `detail_avis` VALUES (2,'001','','Ambulance type B tout terrain',1.000,1.000,'NB','NB','Manque 2 bouteille Oxigene',5,'conforme');
/*!40000 ALTER TABLE `detail_avis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_accounts_customuser_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_customuser` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (6,'accounts','customuser'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(10,'core','article'),(15,'core','articlecaracteristique'),(11,'core','articlefamily'),(14,'core','articleimage'),(12,'core','articlesql'),(24,'core','avisarrivee'),(34,'core','barremage'),(13,'core','caracteristique'),(35,'core','citerne'),(7,'core','companyinfo'),(36,'core','consommationcarburant'),(25,'core','detailavis'),(28,'core','engin'),(40,'core','equipement'),(20,'core','etapedossier'),(23,'core','etatb1view'),(30,'core','intervenant'),(37,'core','lectureindex'),(38,'core','lecturejauge'),(39,'core','lecturepompe'),(18,'core','naturestock'),(42,'core','notification'),(8,'core','page'),(9,'core','permissionmatrix'),(31,'core','personnel'),(26,'core','piecejointeavis'),(22,'core','piecejointeetape'),(29,'core','piecejointetache'),(33,'core','planningtache'),(16,'core','serialunit'),(41,'core','service'),(21,'core','suividossier'),(32,'core','tache'),(27,'core','tiers'),(17,'core','typemouvement'),(19,'core','valeurarticle'),(5,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-08-13 08:50:27.889920'),(2,'contenttypes','0002_remove_content_type_name','2025-08-13 08:50:30.110924'),(3,'auth','0001_initial','2025-08-13 08:50:33.598341'),(4,'auth','0002_alter_permission_name_max_length','2025-08-13 08:50:34.697711'),(5,'auth','0003_alter_user_email_max_length','2025-08-13 08:50:34.736887'),(6,'auth','0004_alter_user_username_opts','2025-08-13 08:50:34.778511'),(7,'auth','0005_alter_user_last_login_null','2025-08-13 08:50:34.841816'),(8,'auth','0006_require_contenttypes_0002','2025-08-13 08:50:34.897654'),(9,'auth','0007_alter_validators_add_error_messages','2025-08-13 08:50:34.965611'),(10,'auth','0008_alter_user_username_max_length','2025-08-13 08:50:35.032529'),(11,'auth','0009_alter_user_last_name_max_length','2025-08-13 08:50:35.092413'),(12,'auth','0010_alter_group_name_max_length','2025-08-13 08:50:35.236468'),(13,'auth','0011_update_proxy_permissions','2025-08-13 08:50:35.299991'),(14,'auth','0012_alter_user_first_name_max_length','2025-08-13 08:50:35.365548'),(15,'accounts','0001_initial','2025-08-13 08:50:40.177129'),(16,'admin','0001_initial','2025-08-13 08:50:42.378690'),(17,'admin','0002_logentry_remove_auto_add','2025-08-13 08:50:42.419513'),(18,'admin','0003_logentry_add_action_flag_choices','2025-08-13 08:50:42.528761'),(19,'sessions','0001_initial','2025-08-13 08:50:43.192558'),(20,'core','0001_initial','2025-08-14 07:45:29.362059'),(21,'core','0002_article_articlefamily','2025-09-05 09:58:41.694104'),(22,'core','0003_alter_articlefamily_options_and_more','2025-09-05 15:20:20.219016'),(23,'core','0004_remove_articlefamily_created_at_and_more','2025-09-05 15:29:22.234426'),(24,'core','0005_alter_articlefamily_options_articlefamily_full_code','2025-09-06 06:55:48.775074'),(25,'core','0006_articlesql_caracteristique','2025-09-07 10:24:11.932406'),(26,'core','0007_alter_caracteristique_nom','2025-09-08 10:44:25.919927'),(27,'core','0008_alter_caracteristique_options_and_more','2025-09-08 10:44:32.593494'),(28,'core','0009_caracteristique_parent_and_more','2025-09-09 06:24:31.988269'),(29,'core','0010_articleimage_articlecaracteristique','2025-09-10 15:40:11.203402'),(30,'core','0011_serialunit_delete_article_alter_articleimage_image_and_more','2025-09-15 09:58:34.700235'),(31,'core','0012_typemouvement','2025-09-15 10:06:42.322153'),(32,'core','0013_naturestock','2025-10-07 06:54:16.758023'),(33,'core','0014_valeurarticle','2025-10-07 08:50:04.799399'),(34,'core','0015_etapedossier','2025-10-07 09:11:23.760552'),(35,'core','0016_etapedossier_influence','2025-10-07 09:32:44.752502'),(36,'core','0017_suividossier','2025-10-30 14:13:15.991082'),(37,'core','0018_remove_suividossier_email_suividossier_email_data','2025-10-31 06:57:30.003424'),(38,'core','0019_alter_suividossier_date_etape_piecejointeetape','2025-10-31 10:44:39.713254'),(40,'core','0020_etatb1view','2025-11-01 15:43:22.713890'),(41,'core','0021_avisarrivee_alter_etatb1view_item_detailavis','2025-11-03 07:39:28.589988'),(42,'core','0022_remove_avisarrivee_date_com_avisarrivee_dat_com_and_more','2025-11-03 15:33:48.171437'),(43,'core','0023_detailavis_conformite','2025-11-04 10:29:21.557534'),(44,'core','0024_suividossier_date_avis_suividossier_bct_and_more','2025-11-05 07:06:54.927821'),(45,'core','0025_rename_date_avis_suividossier_date_avis','2025-11-05 09:24:07.461253'),(46,'core','0026_piecejointeavis','2025-11-05 14:06:55.784371'),(47,'core','0027_alter_detailavis_conformite','2025-11-06 13:55:41.676278'),(48,'core','0028_alter_suividossier_influence_sur_dossier','2025-11-06 16:11:43.486569'),(49,'core','0029_personnel_tache_tiers_piecejointetache_engin_and_more','2025-11-07 07:54:44.005832'),(50,'core','0030_alter_tiers_type_tiers','2025-11-07 13:21:03.892306'),(51,'core','0031_citerne_planningtache_tache_planning_barremage','2025-11-08 10:14:38.538460'),(52,'core','0032_alter_engin_options_remove_engin_tache_engin_actif_and_more','2025-11-08 16:00:19.824627'),(53,'core','0033_lecturejauge_lecturepompe','2025-11-09 06:31:44.308145'),(54,'core','0034_alter_planningtache_options_planningtache_libelle','2025-11-09 08:26:55.032431'),(55,'core','0035_equipement_engin_numero_bp_and_more','2025-11-09 08:56:04.802057'),(56,'core','0036_alter_tache_planning','2025-11-09 10:35:42.181861'),(57,'core','0037_service_engin_created_at_and_more','2025-11-10 06:27:41.653036'),(58,'core','0038_alter_service_options_notification','2025-11-10 15:08:07.394001');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('0wdx6ai829zbvb1lx3qg6bg4xlsgdc9g','.eJxVjMsOwiAUBf-FtSE8hbh07zcQ7gOpGkhKu2r8d23ShW7PzJxNpLwuNa2D5zSRuAgtTr8bZHxy2wE9crt3ib0t8wRyV-RBh7x14tf1cP8Oah71W1t0hQwYVM5qrzAihAAl5EIQwZIxGJ33wCUGzdHCGYxDtMCsXFBKvD_9yzh8:1unBJV:VryrdZKxYPamU_v5uiR7rIWWI2R09l73l4iIrgxuOOU','2025-08-30 07:26:53.713049'),('4bhniwes9n6cp2jli4lvxk0o1z9kb9up','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v3qKa:O7lWY3qBuqBhzEOAP1RL8s-r5pwRUaEjLdDWXIk3tNo','2025-10-15 06:28:52.898575'),('6k0dfmb5l7m7ak1w5jr0v0z95m0lbbe9','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uwybg:uJ01m5OqlUa2kVatlIehEimQNUhiXEvN6-f2B2ifyrs','2025-09-26 07:54:08.681487'),('6k0ez2fv2sdw5hvo2rk5or9gt9gfiyfx','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uwEcx:aLFNQT8EXMgUmnIEi6UvKbYSx-9t9GEd8yLpCD1_xQ4','2025-09-24 06:48:23.921826'),('7x7u7ar30wmshcw5oam6gxwt6x8zd8ye','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v6V9y:j4GQfi5sv_bUhmicmA4PdTD1UvAGVUWmjxHUuY8SEgc','2025-10-22 14:28:54.046908'),('blian3xsd6jfkb8ljbljdizlm3i8hxv1','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1vGJur:IO3UrNi9eSGPGDSA-dYVUCce5lDbNaWStWGDs_yspyg','2025-11-18 16:29:53.757485'),('cwsy9083fadw2gvb9drlt4qsldh07354','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1vHJ9c:mp4hX-M6zvap6Wj0jhDUtAKRoyVFZQQ0PYDOBIX6jVo','2025-11-21 09:53:12.155332'),('cya2mftllydndh8n6xiqlisfq4masp65','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1vHbqT:er4Zxrt5yb8GSJZtst6FqTfshxV5Kg0YOGxmDJxjPg0','2025-11-22 05:50:41.489921'),('f2vlge53u12uj803dksouana0hm12wur','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v6Q9b:nkIRs4K99ph9vmoqrHVRmgAEokaXjhMcII2c1r92Qqw','2025-10-22 09:08:11.321789'),('gsqapa7gqed5ocei6g4jrxjady5f515n','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1vFDxg:uKslSHppKVv-8LULXQPE-kXtQ_FDCsFImav7k8XYnTw','2025-11-15 15:56:16.578154'),('itery4n6lir7m15b151054znkjkyu652','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v6ULS:25AkssfYLcjVNrU4Gsy3hAv6uzaM_XXP1lqKPoj8PFU','2025-10-22 13:36:42.450003'),('jfveot7ic3pd6dyddwlzvfkhqkatzurq','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v7t1a:OHkTImzrfF6TtFBgzI5iJwMFMDNW3QzdrIKmLFM-3Gc','2025-10-26 10:09:58.551711'),('k830w8x0p7wmpybumi71vftbdwax6v32','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1vDzoK:dOsuW1lVROdhBf7rvLWSYawpvybd0_kEcrU1JCMxYsI','2025-11-12 06:37:32.642338'),('ki8p3uhmyywbtnp8szyte0jhsvqgy47z','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v4yUt:oZNgD8-H4Ht38-nEpPmtKOy34JBqG748nFnj_Z7SN70','2025-10-18 09:24:11.826380'),('kk72t6f9upxtywpxmqtvkgpddvukj04f','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uvujb:HntjRgEPw1CcAKJ8JhMnwiNIl2r3e-SIUtZpbZO74uk','2025-09-23 09:33:55.836459'),('krn1cy99jcsx6wspwa5yugulqkp0aiog','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uvuWT:BqsB6t6cZBKfpAeeVtVGRSSRlnIJoF3Cr4-ORLmfdJs','2025-09-23 09:20:21.296807'),('mm1h1o5xt0umjjab7nc3dojm9lw4jbtp','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1vHbrk:twnWcIbCAAPNjh1Ypc4loqHOvmDMrXKGp-3B_Vhh6uI','2025-11-22 05:52:00.646601'),('otqr3oeums8qtmof8mk0uybctq4pjewz','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1vGXZT:uXJE6ewhlArOS5i-l0zBsGo_gx2S3IgfBbQC7bAugaE','2025-11-19 07:04:43.047531'),('oucp4znkbeu4w60b6tfn3dbha76b57hg','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uwHH1:KVJMjeo1Ws65z194TL9sBO5A3_13wNbHXXxR0bR1XBk','2025-09-24 09:37:55.433520'),('qcfkua4dgqsezclv5gwjsb7p7hi3uc40','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v6OcD:5crdIqb_gY_iCAKYMKm5fNFWohRppdLGHZscyzpO0pQ','2025-10-22 07:29:37.635797'),('su65qionnkny66dj4x2yfiyhn4rqoedm','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v63kg:R4wD-Cd5OpH66XyY925w8MpoOs679KCRg5o1qVsnWXM','2025-10-21 09:12:58.009926'),('sv8lgjskwnlyeahlhe6bvhm70br1wtzf','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1vFnmT:EEmZEZxcoFb3RishXVsZM8ccqC41K_HGwdY9mDkQ_i0','2025-11-17 06:11:05.152787'),('vfn91apd0l5qfhf8i2k58d1jid83e93e','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v7WxS:RRFiGK-UwK5Lv1JE0xE4EVUGSLAzFIC23brBSJEwfI8','2025-10-25 10:36:14.906716'),('vp0dw3286qy3jy4zzp5y26zxexh05x5y','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1vGJoS:O_BVUR4ONs7LUBRK39sEgOvt3wAMvMW814NAjt54fqA','2025-11-18 16:23:16.223355'),('wmphrb1j08tdv4u9bmk6kgdouq5m64n9','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v4K3S:SxDheCLj2rFfSp_VSTsRHSfmxGyxdSpzIU0gHaNBvJ0','2025-10-16 14:13:10.746885'),('xepbjcl2sdy9wz9lrh4zf9lwq5fftd2z','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v68bB:Wf2ivj9qMj1WNuAXItTbLojvwaKRdgeCc7tseKlyZBM','2025-10-21 14:23:29.187443'),('xzsorzpw2fwtwu6hfe5d3xxp9srigglw','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uyS26:2c8Nkqou4LsyW2bdOJoHCIXONwR6-074alIwABub-_c','2025-09-30 09:31:30.451241');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `engin`
--

DROP TABLE IF EXISTS `engin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `engin` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `libelle` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `numero_serie` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `actif` tinyint(1) NOT NULL,
  `capacite_reservoir` decimal(6,1) DEFAULT NULL,
  `immatriculation` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `index_initial` decimal(12,1) NOT NULL,
  `type_carburant` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type_engin` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `numero_bp` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `date_1ere_mise_en_circulation` date DEFAULT NULL,
  `date_derniere_visite` date DEFAULT NULL,
  `genre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `marque` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `observations` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `puissance_fiscale` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `situation` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `service_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `engin_service_id_09fdca0b_fk_service_id` (`service_id`),
  CONSTRAINT `engin_service_id_09fdca0b_fk_service_id` FOREIGN KEY (`service_id`) REFERENCES `service` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `engin`
--

LOCK TABLES `engin` WRITE;
/*!40000 ALTER TABLE `engin` DISABLE KEYS */;
INSERT INTO `engin` VALUES (1,'Pompe Gasoil Ord Station Service','',1,NULL,'',5719065.0,'gasoil','voiture','','2025-11-10 06:27:36.270267',NULL,NULL,'','','','','en_service','2025-11-10 06:27:39.989030',NULL),(2,'Pompe Gasoil SS Station Service','',1,NULL,'',1032505.0,'essence','voiture','','2025-11-10 06:27:36.270267',NULL,NULL,'','','','','en_service','2025-11-10 06:27:39.989030',NULL),(4,'MITSU PAJERO V76W V76WLNDFL','JMYLNV76W6J000347',1,NULL,'86665 RS',0.0,'gasoil','autre','620396','2025-11-10 06:31:55.856897','2005-12-02','2022-03-29','AMBULANCE 5 PLACES','MITSU PAJERO V76W','ETAT MOYEN','11 CV GASOIL','en_service','2025-11-10 06:31:55.856951',2),(5,'MITSUBISHI L200 KB4TNJNML','MMNBJNKB409D020400',1,NULL,'112767 RS',0.0,'gasoil','autre','621523','2025-11-10 06:31:56.042357','2011-01-24','2016-08-06','5 PLACES / 1T160','MITSUBISHI L200','MAUVAIS ETAT','10 CV GASOIL','en_service','2025-11-10 06:31:56.042410',3),(6,'MITSUBISHI L200 KB4TNJNML','MMNBJNKB409D027057',1,NULL,'112768 RS',0.0,'gasoil','autre','621524','2025-11-10 06:31:56.224896','2011-01-24','2016-08-06','5 PLACES / 1T160','MITSUBISHI L200','MAUVAIS ETAT','10 CV GASOIL','en_service','2025-11-10 06:31:56.224948',4),(7,'MAZDA BT50 UNY0W44','MM7UNY0W4D0924965',1,NULL,'8244 TU 165',0.0,'gasoil','autre','622257','2025-11-10 06:31:56.316783','2013-05-15','2020-02-13','5 PLACES','MAZDA BT50','MAUVAIS ETAT','10 CV GASOIL','en_service','2025-11-10 06:31:56.316835',5),(8,'MAZDA BT50 UNY0W44','MM7UNY0W4D0924944',1,NULL,'8254 TU 165',0.0,'gasoil','autre','622259','2025-11-10 06:31:56.424828','2013-05-15','2020-12-18','5 PLACES ','MAZDA BT50','MAUVAIS ETAT','10 CV GASOIL','en_service','2025-11-10 06:31:56.424882',6),(9,'MAZDA BT50 UNY0W44','MM7UNYOW4D0924942',1,NULL,'8258 TU 165',0.0,'gasoil','autre','622260','2025-11-10 06:31:56.514828','2013-05-15','2020-02-15','5 PLACES','MAZDA BT50','MAUVAIS ETAT','10 CV GASOIL','en_service','2025-11-10 06:31:56.514858',7),(10,'MAZDA BT50 UNY0W44','MM7UNY0W4D0924917',1,NULL,'8259 TU 165',0.0,'gasoil','autre','622261','2025-11-10 06:31:56.733480','2013-05-15','2021-03-13','5 PLACESS ','MAZDA BT50','MAUVAIS ETAT','10 CV GASOIL','en_service','2025-11-10 06:31:56.733533',8),(11,'MAZDA BT50 UNY0W44','MM7UNYOW4E0938007',1,NULL,'5177 TU 176',0.0,'gasoil','autre','622736','2025-11-10 06:31:56.833406','2014-10-06','2020-12-07','5 PLACES','MAZDA BT50','ETAT MOYEN','10 CV GASOIL','en_service','2025-11-10 06:31:56.833459',9),(12,'MAZDA BT50 UNY0W44','MM7UNYOW4E0938029',1,NULL,'5188 TU 176',0.0,'gasoil','autre','622741','2025-11-10 06:31:56.941900','2014-10-06','2020-02-15','5 PLACESS ','MAZDA BT50','ETAT MOYEN','10 CV GASOIL','en_service','2025-11-10 06:31:56.941953',10),(13,'MAZDA BT50 UNY0W44','MM7UNYOW4E0938996',1,NULL,'4960 TU 178',0.0,'gasoil','autre','622842','2025-11-10 06:31:57.025047','2014-12-30','2020-12-11','5 PLACESS ','MAZDA BT50','MAUVAIS ETAT','10 CV GASOIL','en_service','2025-11-10 06:31:57.025109',11),(14,'MAZDA UP4DB2M','MM7UP4DB5FW446736',1,NULL,'3424 TU 183',0.0,'gasoil','autre','622852','2025-11-10 06:31:57.130315','2015-08-11','2018-09-17','5 PLACESS ','MAZDA','MAUVAIS ETAT','9 CV GASOIL','en_service','2025-11-10 06:31:57.130331',12),(15,'MAZDA UP4DB2M','MM7UP4DB0FW446496',1,NULL,'3427 TU 183',0.0,'gasoil','autre','622853','2025-11-10 06:31:57.241144','2015-08-11','2021-03-08','5 PLACESS ','MAZDA','ETAT MOYEN','9 CV GASOIL','en_service','2025-11-10 06:31:57.241203',13),(16,'MAZDA UP4DB2M','MM7UP4DB8FW446729',1,NULL,'3430 TU 183',0.0,'gasoil','autre','622854','2025-11-10 06:31:57.342180','2015-08-11','2018-11-24','5 PLACESS ','MAZDA','REVISION MOTEUR','9 CV GASOIL','en_panne','2025-11-10 06:31:57.342234',14),(17,'MAZDA UP4DB2M','MM7UP4DB2FW446712',1,NULL,'3434 TU 183',0.0,'gasoil','autre','622855','2025-11-10 06:31:57.475328','2015-08-11','2020-06-04','5 PLACESS ','MAZDA','MAUVAIS ETAT','9 CV GASOIL','en_service','2025-11-10 06:31:57.475380',15),(18,'MAZDA UP4DB2M','MM7UP4DB4FW446808',1,NULL,'3436 TU 183',0.0,'gasoil','autre','622856','2025-11-10 06:31:57.600619','2015-08-11','2021-03-12','5 PLACESS ','MAZDA','NECESSITE DU TURBO COMPRESSEUR ET DEUX AMORTISSEURS AVANT ','9 CV GASOIL','en_service','2025-11-10 06:31:57.600672',16),(19,'MAZDA UP4DB2M','MM7UP4DB7FW446706',1,NULL,'3438 TU 183',0.0,'gasoil','autre','622857','2025-11-10 06:31:57.661430','2015-08-11','2020-12-18','5 PLACESS ','MAZDA','REVISION MOTEUR','9 CV GASOIL','en_panne','2025-11-10 06:31:57.661490',14),(20,'MAZDA UP4DB2M','MM7UP4DBXFW446800',1,NULL,'3440 TU 183',0.0,'gasoil','autre','622858','2025-11-10 06:31:57.751338','2015-08-11','2021-03-05','5 PLACESS ','MAZDA','REVISION MOTEUR','9 CV GASOIL','en_panne','2025-11-10 06:31:57.751390',17),(21,'MAZDA UP4DB2M','MM7UP4DB1FW446796',1,NULL,'3445 TU 183',0.0,'gasoil','autre','622859','2025-11-10 06:31:57.795038','2015-08-11','2020-11-28','5 PLACESS ','MAZDA','NECESSITE DE TORBO, 4 INJECTEURS ET POMPE D\'INJECTION','9 CV GASOIL','en_panne','2025-11-10 06:31:57.795092',12),(22,'MITSU PAJERO V96W V96WLNDFLAM','JMYLNV96WDJ000364',1,NULL,'153258 RS',0.0,'gasoil','autre','622864','2025-11-10 06:31:57.914465','2015-09-28',NULL,'7 PLACES','MITSU PAJERO V96W','MAUVAIS ETAT','11 CV GASOIL','en_service','2025-11-10 06:31:57.914483',18),(23,'PEUGEOT BIPPER  AJ8HSC','VF3AJ8HSCF8657551',1,NULL,'6918 TU 187',0.0,'gasoil','autre','622959','2025-11-10 06:31:57.995505','2016-03-04',NULL,'5 PLACESS ','PEUGEOT BIPPER ','NECESSITE REFREGIRENT','6 CV GASOIL','en_panne','2025-11-10 06:31:57.995557',16),(24,'MAZDA UP4DB2M','MM7UP4DB5GW540603',1,NULL,'7424 TU 189',0.0,'gasoil','autre','622976','2025-11-10 06:31:58.269885','2016-05-30',NULL,'5 PLACESS ','MAZDA','NECESSITE KIT D\'EMBRAYAGE','9 CV GASOIL','en_panne','2025-11-10 06:31:58.269940',19),(25,'MAZDA UP4DB2M','MM7UP4DB4GW540611',1,NULL,'7434 TU 189',0.0,'gasoil','autre','622978','2025-11-10 06:31:58.425857','2016-05-30','2020-06-03','5 PLACESS ','MAZDA','MAUVAIS ETAT','9 CV GASOIL','en_service','2025-11-10 06:31:58.425909',20),(26,'MAZDA UP4DB2M','MM7UP4DB8GW540594',1,NULL,'7438 TU 189',0.0,'gasoil','autre','622984','2025-11-10 06:31:58.511883','2016-05-30','2020-02-13','5 PLACESS ','MAZDA','REVISION MOTEUR','9 CV GASOIL','en_panne','2025-11-10 06:31:58.511934',5),(27,'MAZDA UP4DB2M','MM7UP4DB3GW540602',1,NULL,'7441 TU 189',0.0,'gasoil','autre','622980','2025-11-10 06:31:58.601828','2016-05-30','2020-12-03','5 PLACESS ','MAZDA','MAUVAIS ETAT','9 CV GASOIL','en_service','2025-11-10 06:31:58.601878',21),(28,'MAZDA UP4DB2M','MM7UP4DB0GW540606',1,NULL,'7445 TU 189',0.0,'gasoil','autre','622981','2025-11-10 06:31:58.654172','2016-05-30','2020-12-09','5 PLACESS ','MAZDA','ETAT MOYEN','9 CV GASOIL','en_service','2025-11-10 06:31:58.654223',19),(29,'MAZDA UP4DB2M','MM7UP4DB3HW655055',1,NULL,'5682 TU 196',0.0,'gasoil','autre','623054','2025-11-10 06:31:58.742804','2017-04-05','2020-11-12','5 PLACESS ','MAZDA','ETAT MOYEN','9 CV GASOIL','en_service','2025-11-10 06:31:58.742857',22),(30,'MAZDA UP4DB2M','MM7UP4DB6HW655065',1,NULL,'5684 TU 196',0.0,'gasoil','autre','623053','2025-11-10 06:31:58.842777','2017-04-05','2019-07-16','5 PLACES ','MAZDA','REVISION MOTEUR','9 CV GASOIL','en_panne','2025-11-10 06:31:58.842829',23),(31,'MAZDA UP4DB2M','MM7UP4DB8HW655066',1,NULL,'5685 TU 196',0.0,'gasoil','autre','623051','2025-11-10 06:31:58.984640','2017-04-05','2021-11-20','5 PLACESS ','MAZDA','ETAT MOYEN','9 CV GASOIL','en_service','2025-11-10 06:31:58.984693',24),(32,'MAZDA UP4DB2M','MM7UP4DB5HW655073',1,NULL,'5687 TU 196',0.0,'gasoil','autre','','2025-11-10 06:31:59.100823','2017-04-05','2020-12-03','5 PLACESS ','MAZDA','ETAT MOYEN','9 CV GASOIL','en_service','2025-11-10 06:31:59.100871',25),(33,'MAZDA UP4DB2M','MM7UP4DB3HW655041',1,NULL,'5692 TU 196',0.0,'gasoil','autre','623050','2025-11-10 06:31:59.226448','2017-04-05','2019-11-06','5 PLACESS ','MAZDA','ETAT MOYEN','9 CV GASOIL','en_service','2025-11-10 06:31:59.226500',26),(34,'MITSU PAJERO  V96WLNDFLAM','JMYLNV96WHJ000458',1,NULL,'174484 RS',0.0,'gasoil','autre','','2025-11-10 06:31:59.295600','2017-11-23',NULL,'7 PLACES','MITSU PAJERO ','NECESSITE DE CULASSE ','11 CV GASOIL','en_panne','2025-11-10 06:31:59.295658',12),(35,'MITSU PAJERO  V96WLNDFLAM','JMYLNV96WHJ000459',1,NULL,'174485 RS',0.0,'gasoil','autre','','2025-11-10 06:31:59.409875','2017-11-23',NULL,'7 PLACES','MITSU PAJERO ','ETAT MOYEN','11 CV GASOIL','en_service','2025-11-10 06:31:59.409929',27),(36,'TOYOTA GUN125LDNFXHN','AHTFB8CD103873937',1,NULL,'1630 TU 213',0.0,'gasoil','autre','','2025-11-10 06:31:59.521307','2019-10-18','2021-11-18','5 PLACES ','TOYOTA','NECESSITE BOITE DE TRANSFERT','8 CV GASOIL','en_panne','2025-11-10 06:31:59.521358',3),(37,'TOYOTA GUN125LDNFXHN','AHTFB8CD803873806',1,NULL,'1631 TU 213',0.0,'gasoil','autre','','2025-11-10 06:31:59.634892','2019-10-18','2021-12-15','5 PLACES ','TOYOTA','ETAT MOYEN','8 CV GASOIL','en_service','2025-11-10 06:31:59.634946',28),(38,'TOYOTA GUN125LDNFXHN','AHTFB8CD903874186',1,NULL,'1645 TU 213',0.0,'gasoil','autre','','2025-11-10 06:31:59.688346','2019-10-18',NULL,'5 PLACES ','TOYOTA','ETAT MOYEN','8 CV GASOIL','en_service','2025-11-10 06:31:59.688402',12),(39,'TOYOTA GUN125LDNFXHN','AHTFB8CD603873593',1,NULL,'1647 TU 213',0.0,'gasoil','autre','','2025-11-10 06:31:59.796184','2019-10-18',NULL,'5 PLACES ','TOYOTA','ETAT MOYEN','8 CV GASOIL','en_service','2025-11-10 06:31:59.796239',21),(40,'TOYOTA GUN125LDNFXHN','AHTFB8CD803873157',1,NULL,'1648 TU 213',0.0,'gasoil','autre','','2025-11-10 06:31:59.919166','2019-10-18','2021-11-13','5 PLACES ','TOYOTA','ETAT MOYEN','8 CV GASOIL','en_service','2025-11-10 06:31:59.919220',29),(41,'TOYOTA GUN125LDNFXHN','AHTFB8CD303873504',1,NULL,'1649 TU 213',0.0,'gasoil','autre','','2025-11-10 06:32:00.039845','2019-10-18',NULL,'5 PLACES ','TOYOTA','ETAT MOYEN','8 CV GASOIL','en_service','2025-11-10 06:32:00.039862',30),(42,'TOYOTA GUN125LDNFXHN','AHTFB8CD603874260',1,NULL,'1650 TU 213',0.0,'gasoil','autre','','2025-11-10 06:32:00.123575','2019-10-18',NULL,'5 PLACES ','TOYOTA','ETAT MOYEN','8 CV GASOIL','en_service','2025-11-10 06:32:00.123629',12),(43,'TOYOTA GUN125LDNFXHN','AHTFB8CD503873682',1,NULL,'1651 TU 213',0.0,'gasoil','autre','','2025-11-10 06:32:00.226854','2019-10-18',NULL,'5 PLACES ','TOYOTA','ETAT MOYEN','8 CV GASOIL','en_service','2025-11-10 06:32:00.226909',31),(44,'TOYOTA GUN125LDNFXHN','AHTFB8CD803873711',1,NULL,'1652 TU 213',0.0,'gasoil','autre','','2025-11-10 06:32:00.303487','2019-10-18',NULL,'5 PLACES ','TOYOTA','ETAT MOYEN','8 CV GASOIL','en_service','2025-11-10 06:32:00.303539',5);
/*!40000 ALTER TABLE `engin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipement`
--

DROP TABLE IF EXISTS `equipement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipement` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `libelle` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type_equipement` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `numero_serie` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `numero_bp` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `actif` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipement`
--

LOCK TABLES `equipement` WRITE;
/*!40000 ALTER TABLE `equipement` DISABLE KEYS */;
INSERT INTO `equipement` VALUES (1,'Pompe Gasoil Ord Station Service','pompe_distribution','','',1),(3,'Pompe Gasoil SS Station Service','pompe_distribution','','',1);
/*!40000 ALTER TABLE `equipement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etape_dossier`
--

DROP TABLE IF EXISTS `etape_dossier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etape_dossier` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code_etape` smallint unsigned NOT NULL,
  `libelle_etape` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `influence` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_etape` (`code_etape`),
  CONSTRAINT `etape_dossier_chk_1` CHECK ((`code_etape` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etape_dossier`
--

LOCK TABLES `etape_dossier` WRITE;
/*!40000 ALTER TABLE `etape_dossier` DISABLE KEYS */;
INSERT INTO `etape_dossier` VALUES (1,1,'Etablissement BC / Contrat','autre'),(2,2,'Reception Materiel au Magasin Tunis','instance'),(3,3,'Reception Materiel au Magasin EBC','instance'),(4,4,'Etablissement Avis d\'arrivée - Email','instance'),(5,5,'Reception Partiel','instance'),(6,6,'Reception Partiel B1 Etablie','instance'),(7,7,'Reception Total','instance'),(8,8,'Reception Total B1 Etablie','cloture'),(9,9,'Litige-Materiel Non Conforme','litige'),(10,10,'Assurance-Materiel Endommage','instance'),(12,11,'Retour Materiel','instance');
/*!40000 ALTER TABLE `etape_dossier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etatb1view`
--

DROP TABLE IF EXISTS `etatb1view`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etatb1view` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `doc_ref` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_ref` date DEFAULT NULL,
  `item` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cod_art` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `lib_art` longtext COLLATE utf8mb4_unicode_ci,
  `qte_commande` decimal(15,3) DEFAULT NULL,
  `nature_bon` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_b` date NOT NULL,
  `numero_bon` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `qte_recept` decimal(15,3) DEFAULT NULL,
  `lib_um_com` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `lib_um` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `valeur_tot` decimal(18,3) DEFAULT NULL,
  `class_cout` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `empl` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `old_qte` decimal(15,3) DEFAULT NULL,
  `val_art` decimal(18,3) DEFAULT NULL,
  `num_facture` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `numero_bp` longtext COLLATE utf8mb4_unicode_ci,
  `taux_change` decimal(10,6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `etat_b1_primary_key` (`date_b`,`numero_bon`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etatb1view`
--

LOCK TABLES `etatb1view` WRITE;
/*!40000 ALTER TABLE `etatb1view` DISABLE KEYS */;
INSERT INTO `etatb1view` VALUES (1,'0115/2023L','1900-01-01','001','262110240K','OXYGENE INDUSTRIEL POUR SOUDURE EN BOUTEILLE      ',34.000,'B1','2023-07-31','072861',360.400,'NB        ','M3        ',2567.748,'0271','KIOSK',-137.800,1.000,'BL N°: D52T23-002344  DU 29/07/2023               ','',NULL),(2,'0115/2023L','1900-01-01','002','248160017Z','ACETYLENE POUR SOUDURE EN BOUTEILLE               ',13.000,'B1','2023-07-31','072862',78.000,'NB        ','M3        ',3607.695,'0271','KIOSK',-60.000,1.000,'BL N°: D52T23-002344  DU 29/07/2023               ','',NULL),(3,'0115/2023L','1900-01-01','003','262390312L','CO2 EN BOUTEILLE DE 30 KG                         ',1.000,'B1','2023-07-31','072863',30.000,'NB        ','KG        ',134.120,'0271','KIOSK',30.000,1.000,'BL N°: D52T23-002344  DU 29/07/2023               ','',NULL),(5,'0011/2004L','2004-01-08','001','398774023A','ELECTRODE 2.5X350MM OK48-04 ESAB                  ',967.500,'B1','2004-02-23','045514',967.500,NULL,'KG        ',4106.070,'0257','ZNREC',81.700,1.000,' BL N¦ 2940 DU 20/01/04                           ',NULL,NULL),(6,'0011/2004L','1900-01-01','002','398774035N','ELECTRODE 3.25X450MM OK48-00 ESAB                 ',486.000,'B1','2004-02-27','045515',486.000,NULL,'KG        ',1669.896,'0257','Z132G',-486.000,1.000,' BL N¦ 2940 DU 20/01/04                           ',NULL,NULL),(7,'0011/2004L','1900-01-01','003','398774203W','ELECTRODE 3.25X350MM PIPEWELD 6010 ESAB           ',640.000,'B1','2004-02-27','045516',639.400,NULL,'KG        ',2753.256,'0257','ZNREC',997.400,1.000,' BL N¦ 2940 DU 20/01/04                           ',NULL,NULL),(9,'0115/2023L','1900-01-01','004','262110219M','OXYGENE MEDICAL EN BOUTEILLE                      ',1.000,'B1','2023-07-31','072864',1.100,'NB        ','M3        ',53.276,'0271','KIOSK',41.300,1.000,'BL N°: D52T23-002344  DU 29/07/2023               ','',NULL),(10,'0170/2025L','2025-07-24',NULL,'703034114Q','MELANGEUR DE LAVABO CHROME                        ',NULL,'B1','2025-10-19','074674',5.000,NULL,'NB        ',393.865,'0238','B206D',-1.000,1.000,'BL N° BL25/02267 DU 25/08/2025',NULL,NULL),(11,'0170/2025L','2025-07-24',NULL,'703930020B','KIT DOUCHE CHR DOUCHETTE, FLEXIBLE ET SUPPORT     ',NULL,'B1','2025-10-19','074675',11.000,NULL,'NB        ',351.365,'0238','B207G',-1.000,1.000,'BL N° BL25/02267 DU 25/08/2025',NULL,NULL),(12,'0170/2025L','2025-07-24',NULL,'352629040K','RACCORD DROIT A VISSER 3/8 MALE MULTICOUCHE       ',NULL,'B1','2025-10-19','074676',4.000,NULL,'NB        ',18.015,'0238','B211I',6.000,1.000,'BL N° BL25/02267 DU 25/08/2025',NULL,NULL),(13,'0170/2025L','2025-07-24',NULL,'703938117C','FLEXIBLE DE TOILETTE CHROME                       ',NULL,'B1','2025-10-19','074677',11.000,NULL,'NB        ',106.499,'0238','B207I',0.000,1.000,'BL N° BL25/02267 DU 25/08/2025',NULL,NULL),(14,'0170/2025L','2025-07-24',NULL,'409003717H','ROBINET DE TOILETTE CHROME                        ',NULL,'B1','2025-10-19','074678',11.000,NULL,'NB        ',184.223,'0238','B204I',-1.000,1.000,'BL N° BL25/02267 DU 25/08/2025',NULL,NULL),(15,'0170/2025L','2025-07-24',NULL,'703989995R','CANIVEAU POUR DOUCHE MELLEGUE 40 CM               ',NULL,'B1','2025-10-19','074679',12.000,NULL,'NB        ',158.995,'0238','B207E',0.000,1.000,'BL N° BL25/02267 DU 25/08/2025',NULL,NULL),(16,'0170/2025L','2025-07-24',NULL,'703169952Q','SIPHON EXTENSIBLE 33                              ',NULL,'B1','2025-10-19','074680',12.000,NULL,'NB        ',45.847,'0238','B203H',-1.000,1.000,'BL N° BL25/02267 DU 25/08/2025',NULL,NULL),(17,'0170/2025L','2025-07-24',NULL,'702823615M','MECANISME DE CHASSE EN PLASTIQUE A BOUTON         ',NULL,'B1','2025-10-19','074681',6.000,NULL,'NB        ',161.696,'0238','B201C',0.000,1.000,'BL N° BL25/02267 DU 25/08/2025',NULL,NULL),(18,'0170/2025L','2025-07-24',NULL,'703990014M','JEUX DE FIXATION LAVABO                           ',NULL,'B1','2025-10-19','074682',16.000,NULL,'NB        ',18.323,'0238','B202G',0.000,1.000,'BL N° BL25/02267 DU 25/08/2025',NULL,NULL),(19,'0170/2025L','2025-07-24',NULL,'352629005X','RACCORD DROIT A VISSER 1/2 MALE  TUBE MULTICOUCHE ',NULL,'B1','2025-10-19','074683',46.000,NULL,'NB        ',222.631,'0238','B211D',0.000,1.000,'BL N° BL25/02267 DU 25/08/2025',NULL,NULL),(20,'0170/2025L','2025-07-24',NULL,'352629023R','RACCORD DROIT A VISSER 3/4 MALE  TUBE MULTICOUCHE ',NULL,'B1','2025-10-19','074684',40.000,NULL,'NB        ',293.748,'0238','B211I',0.000,1.000,'BL N° BL25/02267 DU 25/08/2025',NULL,NULL),(21,'0010/2024E','2024-03-05',NULL,'338920227B','ANN.R27 SECT.OVALE ASA B16.20 FER ARMCO CADM.     ',NULL,'B1','2025-05-30','074334',30.000,NULL,'NB        ',2539.856,'0211','C001E',-7.000,1.000,'BL N° SITEP-0003-2025 du 16/05/2025.',NULL,NULL),(22,'0010/2024E','2024-03-05',NULL,'338920250B','ANN.R50 SECT.OVALE ASA B16.20 FER ARMCO CADM.     ',NULL,'B1','2025-05-30','074335',20.000,NULL,'NB        ',4292.545,'0211','C002F',-1.000,1.000,'BL N° SITEP-0003-2025 du 16/05/2025.',NULL,NULL),(23,'0010/2024E','2024-03-05',NULL,'332029207M','BRIDE 2\"1/16 3000PSI R24 2\"7/8EU                  ',NULL,'B1','2025-05-30','074336',5.000,NULL,'NB        ',1474.998,'0211','B043G',0.000,1.000,'BL N°SITEP-0003-2025 du 16/05/2025.',NULL,NULL),(24,'0010/2024E','2024-03-05',NULL,'332029209P','BRIDE 2\"9/16 3000PSI R24 2\"7/8EU                  ',NULL,'B1','2025-05-30','074337',5.000,NULL,'NB        ',1893.416,'0211','B060H',0.000,1.000,'BL N°SITEP-0003-2025 du 16/05/2025',NULL,NULL),(25,'0010/2024E','2024-03-05',NULL,'416720678J','FLANGE 3 1/8x2 7/8EUE 3000PSI WP TBA PMP REDA     ',NULL,'B1','2025-05-30','074338',5.000,NULL,'NB        ',3476.781,'0211','B061G',0.000,1.000,'BL N° SITEP-0003-2025 du 16/05/2025.',NULL,NULL),(26,'0010/2024E','2024-03-05',NULL,'416720679K','FLANGE 3 1/8x2 7/8EUE 5000PSI BB PSL1 PR1 U       ',NULL,'B1','2025-05-30','074339',5.000,NULL,'NB        ',2549.639,'0211','B061H',-1.000,1.000,'BL N° SITEP-0003-2025 du 16/05/2025.',NULL,NULL),(27,'0010/2024E','2024-03-05',NULL,'401040002W','ROB.VANNE BRIDE 2\" 1/16 3000 120 90120600 FMC     ',NULL,'B1','2025-05-30','074340',5.000,NULL,'NB        ',16887.222,'0211','P031X',-5.000,2.000,'BL N° SITEP-0003-2025  du 16/05/2025.',NULL,NULL),(28,'0010/2024E','2024-03-05',NULL,'401040004Y','ROB.VANNE BRIDE 2\" 9/16 3000 120 90120616 FMC     ',NULL,'B1','2025-05-30','074341',5.000,NULL,'NB        ',26233.893,'0211','P031X',-5.000,2.000,'BL N° SITEP-0003-2025 du 16/05/2025.',NULL,NULL),(29,'0010/2024E','2024-03-05',NULL,'401040009D','ROB.VANNE OCT 3 1.8 5000 FMC 90010630 MOD.20      ',NULL,'B1','2025-05-30','074342',5.000,NULL,'NB        ',28973.175,'0211','P031X',0.000,1.000,'BL N° SITEP-0003-2025 du16/05/2025.',NULL,NULL),(30,'0111/2025L','2025-05-23','002','741106360R','COMBINAISON DE POMPIER FYRPRO 13152370            ',15.000,'B1','2025-10-15','074643',6.000,'NB        ','NB        ',19200.000,'0240','     ',-6.000,1.000,'FV25026 DU 28/08/2025','',NULL),(31,'0111/2025L','2025-05-23','004','741106362T','CAGOULE DE FEU SAPEUR POMPIE 18018650-K           ',15.000,'B1','2025-10-15','074644',5.000,'NB        ','NB        ',810.000,'0240','     ',-5.000,1.000,'FV25026 DU 28/08/2025','',NULL),(32,'0111/2025L','2025-05-23','006','741106361S','COMBINAISON PROTECTION INCENDIE ALUMINISEE13303900',2.000,'B1','2025-10-15','074645',1.000,'NB        ','NB        ',7500.000,'0240','     ',-1.000,1.000,'FV25026 DU 28/08/2025','',NULL),(33,'0111/2025L','2025-05-23','002','741106360R','COMBINAISON DE POMPIER FYRPRO 13152370            ',15.000,'B1','2025-10-23','074746',9.000,'NB        ','NB        ',28800.000,'0240','     ',-9.000,1.000,'BL N° FV25026 DU 28/08/2025','',NULL),(34,'0111/2025L','2025-05-23','004','741106362T','CAGOULE DE FEU SAPEUR POMPIE 18018650-K           ',15.000,'B1','2025-10-23','074747',10.000,'NB        ','NB        ',1620.000,'0240','     ',-10.000,1.000,'BL N° FV25026 DU 28/08/2025','',NULL),(35,'0111/2025L','2025-05-23','006','741106361S','COMBINAISON PROTECTION INCENDIE ALUMINISEE13303900',2.000,'B1','2025-10-23','074748',1.000,'NB        ','NB        ',7500.000,'0240','     ',-1.000,1.000,'BL N° FV25026 DU 28/08/2025','',NULL),(36,'0104/2008E','2008-06-17','001','666861058B','PROCESSEUR REF.PHASE 1/REV UVL682 VIBRO-METER     ',2.000,'B1','2008-09-27','055656',2.000,'04','NB        ',4117.500,'0255','Z259D',-1.000,1.000,'TU/08/068                                         ',NULL,NULL),(37,'0087/2025L','2025-04-25',NULL,'643081947R','FER A SOUDER JBC C-2BA+PANNE 130W 245V            ',NULL,'B1','2025-05-30','074326',2.000,NULL,'NB        ',2684.228,'0256','ZB02H',-2.000,1.000,'BL N°: BL2507698 du 30/04/2025',NULL,NULL),(38,'0017/2012E','2012-02-14','001','505622580L','INVERTER /ONDULEUR 1500VA /128 VDC  /115 VAC 50HZ ',1.000,'B1','2012-09-10','062502',1.000,'NB        ','NB        ',6920.000,'0255','     ',-1.000,1.000,'86 du18/06/2012                                   ','',NULL),(39,'0153/2025L','2025-07-14',NULL,'000000000A','.                                                 ',NULL,'B1','2025-10-21','074713',1.000,NULL,'NB        ',31660.000,'0255','ZN.PA',-1.000,2.000,'BL N° 0120/2025 DU 29/09/2025',NULL,NULL);
/*!40000 ALTER TABLE `etatb1view` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `intervenant`
--

DROP TABLE IF EXISTS `intervenant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `intervenant` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `personnel_id` bigint DEFAULT NULL,
  `tache_id` bigint NOT NULL,
  `tiers_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `intervenant_personnel_id_548de13b_fk_personnel_id` (`personnel_id`),
  KEY `intervenant_tache_id_5d1e8c5a_fk_tache_id` (`tache_id`),
  KEY `intervenant_tiers_id_31108e38_fk_tiers_id` (`tiers_id`),
  CONSTRAINT `intervenant_personnel_id_548de13b_fk_personnel_id` FOREIGN KEY (`personnel_id`) REFERENCES `personnel` (`id`),
  CONSTRAINT `intervenant_tache_id_5d1e8c5a_fk_tache_id` FOREIGN KEY (`tache_id`) REFERENCES `tache` (`id`),
  CONSTRAINT `intervenant_tiers_id_31108e38_fk_tiers_id` FOREIGN KEY (`tiers_id`) REFERENCES `tiers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `intervenant`
--

LOCK TABLES `intervenant` WRITE;
/*!40000 ALTER TABLE `intervenant` DISABLE KEYS */;
INSERT INTO `intervenant` VALUES (2,'Controle',2,1,NULL);
/*!40000 ALTER TABLE `intervenant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lecture_index`
--

DROP TABLE IF EXISTS `lecture_index`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lecture_index` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date_lecture` date NOT NULL,
  `index_courant` decimal(12,1) NOT NULL,
  `engin_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lecture_index_engin_id_date_lecture_3da698bb_uniq` (`engin_id`,`date_lecture`),
  CONSTRAINT `lecture_index_engin_id_f9fbeb5f_fk_engin_id` FOREIGN KEY (`engin_id`) REFERENCES `engin` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lecture_index`
--

LOCK TABLES `lecture_index` WRITE;
/*!40000 ALTER TABLE `lecture_index` DISABLE KEYS */;
/*!40000 ALTER TABLE `lecture_index` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lecture_jauge`
--

DROP TABLE IF EXISTS `lecture_jauge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lecture_jauge` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date_lecture` date NOT NULL,
  `hauteur_cm` decimal(6,2) NOT NULL,
  `volume_litres` decimal(12,3) DEFAULT NULL,
  `citerne_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lecture_jauge_citerne_id_date_lecture_f52a0f46_uniq` (`citerne_id`,`date_lecture`),
  CONSTRAINT `lecture_jauge_citerne_id_b305ce12_fk_citerne_id` FOREIGN KEY (`citerne_id`) REFERENCES `citerne` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lecture_jauge`
--

LOCK TABLES `lecture_jauge` WRITE;
/*!40000 ALTER TABLE `lecture_jauge` DISABLE KEYS */;
/*!40000 ALTER TABLE `lecture_jauge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lecture_pompe`
--

DROP TABLE IF EXISTS `lecture_pompe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lecture_pompe` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date_lecture` date NOT NULL,
  `index_courant` decimal(12,1) NOT NULL,
  `consommation_depuis_derniere` decimal(12,1) DEFAULT NULL,
  `pompe_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lecture_pompe_pompe_id_date_lecture_2a152088_uniq` (`pompe_id`,`date_lecture`),
  CONSTRAINT `lecture_pompe_pompe_id_b186e6c4_fk_engin_id` FOREIGN KEY (`pompe_id`) REFERENCES `engin` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lecture_pompe`
--

LOCK TABLES `lecture_pompe` WRITE;
/*!40000 ALTER TABLE `lecture_pompe` DISABLE KEYS */;
/*!40000 ALTER TABLE `lecture_pompe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nature_stock`
--

DROP TABLE IF EXISTS `nature_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nature_stock` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code_nature` smallint unsigned NOT NULL,
  `libelle_nature` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_nature` (`code_nature`),
  CONSTRAINT `nature_stock_chk_1` CHECK ((`code_nature` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nature_stock`
--

LOCK TABLES `nature_stock` WRITE;
/*!40000 ALTER TABLE `nature_stock` DISABLE KEYS */;
INSERT INTO `nature_stock` VALUES (1,1,'EXPLOITATION'),(2,2,'AUTRE'),(3,3,'SECURITE'),(4,4,'RESERVATION - E'),(5,5,'RESERVATION - F'),(6,6,'AUTRE'),(7,7,'DECLASSE'),(8,8,'AUTRE');
/*!40000 ALTER TABLE `nature_stock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_read` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `related_tache_id` bigint DEFAULT NULL,
  `related_article` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `notification_user_id_fk` (`user_id`),
  KEY `notification_related_tache_id_fk` (`related_tache_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification`
--

LOCK TABLES `notification` WRITE;
/*!40000 ALTER TABLE `notification` DISABLE KEYS */;
INSERT INTO `notification` VALUES (1,1,'stock_faible','Le stock de \"243000102W\" est critique (0.000 L < 20000.00 L).',0,'2025-11-10 16:22:22.588952',NULL,'243000102W'),(2,1,'stock_faible','Le stock de \"243000312Z\" est critique (0.000 L < 8000.00 L).',0,'2025-11-10 16:22:22.685423',NULL,'243000312Z'),(3,1,'stock_faible','Le stock de \"243000102W\" est critique (0.000 L < 20000.00 L).',0,'2025-11-10 16:30:20.438218',NULL,'243000102W'),(4,1,'stock_faible','Le stock de \"243000312Z\" est critique (0.000 L < 8000.00 L).',0,'2025-11-10 16:30:20.502596',NULL,'243000312Z'),(5,1,'stock_faible','Le stock de \"243000102W\" est critique (0.000 L < 20000.00 L).',0,'2025-11-10 16:40:20.527942',NULL,'243000102W'),(6,1,'stock_faible','Le stock de \"243000312Z\" est critique (0.000 L < 8000.00 L).',0,'2025-11-10 16:40:20.607077',NULL,'243000312Z');
/*!40000 ALTER TABLE `notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `personnel`
--

DROP TABLE IF EXISTS `personnel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `personnel` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `matricule` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telephone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `poste` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `actif` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `matricule` (`matricule`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `personnel`
--

LOCK TABLES `personnel` WRITE;
/*!40000 ALTER TABLE `personnel` DISABLE KEYS */;
INSERT INTO `personnel` VALUES (2,'1815K','ImedEddine','Elmekki','Imed@sitep.com.tn','','Magasin',1,'1815','pbkdf2_sha256$1000000$ZHGFDXY2A3kfLdMVik9Dq9$GgjBQwJVJwn1eA9/JCdBwhy+SqeyOiTcH8I3mPiLdvw=');
/*!40000 ALTER TABLE `personnel` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `sync_personnel_insert` AFTER INSERT ON `personnel` FOR EACH ROW BEGIN
    INSERT INTO accounts_customuser (
        username,
        password,
        email,
        first_name,
        last_name,
        phone,
        is_active,
        is_superuser,  
        is_staff,
        date_joined,
        created_at,
        updated_at
    ) VALUES (
        NEW.username,
        NEW.password,
        NEW.email,
        NEW.nom,
        NEW.prenom,
        NEW.telephone,
        NEW.actif,
        0,
        1,
        NOW(),
        NOW(),
        NOW()
    );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `sync_personnel_update` AFTER UPDATE ON `personnel` FOR EACH ROW BEGIN
    UPDATE accounts_customuser
    SET
        username = NEW.username,
        password = NEW.password,
        email = NEW.email,
        first_name = NEW.nom,
        last_name = NEW.prenom,
        phone = NEW.telephone,
        is_active = NEW.actif,
        updated_at = NOW()
    WHERE username = OLD.username;  -- استخدام OLD لضمان التحديث حتى لو تغير username
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `sync_personnel_delete` AFTER DELETE ON `personnel` FOR EACH ROW BEGIN
    DELETE FROM accounts_customuser
    WHERE username = OLD.username;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `piece_jointe_avis`
--

DROP TABLE IF EXISTS `piece_jointe_avis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `piece_jointe_avis` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fichier` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom_original` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `avis_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `piece_jointe_avis_avis_id_04c5d1db_fk_avis_arrivee_id` (`avis_id`),
  CONSTRAINT `piece_jointe_avis_avis_id_04c5d1db_fk_avis_arrivee_id` FOREIGN KEY (`avis_id`) REFERENCES `avis_arrivee` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `piece_jointe_avis`
--

LOCK TABLES `piece_jointe_avis` WRITE;
/*!40000 ALTER TABLE `piece_jointe_avis` DISABLE KEYS */;
/*!40000 ALTER TABLE `piece_jointe_avis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `piece_jointe_tache`
--

DROP TABLE IF EXISTS `piece_jointe_tache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `piece_jointe_tache` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fichier` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom_original` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `tache_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `piece_jointe_tache_tache_id_4fcb7044_fk_tache_id` (`tache_id`),
  CONSTRAINT `piece_jointe_tache_tache_id_4fcb7044_fk_tache_id` FOREIGN KEY (`tache_id`) REFERENCES `tache` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `piece_jointe_tache`
--

LOCK TABLES `piece_jointe_tache` WRITE;
/*!40000 ALTER TABLE `piece_jointe_tache` DISABLE KEYS */;
/*!40000 ALTER TABLE `piece_jointe_tache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `planning_tache`
--

DROP TABLE IF EXISTS `planning_tache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `planning_tache` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nature` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `delai_repetition` int unsigned NOT NULL,
  `observation` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `libelle` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `planning_tache_chk_1` CHECK ((`delai_repetition` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `planning_tache`
--

LOCK TABLES `planning_tache` WRITE;
/*!40000 ALTER TABLE `planning_tache` DISABLE KEYS */;
INSERT INTO `planning_tache` VALUES (1,'repetitive',30,'Besoin de engin','2025-11-08 13:45:01.142697','2025-11-09 08:42:16.151884','Controle Parc Tube Desemsablement si necessaire');
/*!40000 ALTER TABLE `planning_tache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service`
--

DROP TABLE IF EXISTS `service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `service` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nom` (`nom`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service`
--

LOCK TABLES `service` WRITE;
/*!40000 ALTER TABLE `service` DISABLE KEYS */;
INSERT INTO `service` VALUES (1,'D\'AFFECTATION','Service créé depuis le fichier Excel: D\'AFFECTATION '),(2,'CENTRE MEDICAL','Service créé depuis le fichier Excel: CENTRE MEDICAL'),(3,'PRODUCTION EB 406','Service créé depuis le fichier Excel: PRODUCTION EB 406'),(4,'PRODUCTION 3EME PHASE','Service créé depuis le fichier Excel: PRODUCTION 3EME PHASE'),(5,'FORAGE','Service créé depuis le fichier Excel: FORAGE'),(6,'PRODUCTION EB 407','Service créé depuis le fichier Excel: PRODUCTION EB 407'),(7,'PRODUCTION LAB','Service créé depuis le fichier Excel: PRODUCTION LAB'),(8,'CENTRE HUILE','Service créé depuis le fichier Excel: CENTRE HUILE'),(9,'ENTRETIEN BATIMENT','Service créé depuis le fichier Excel: ENTRETIEN BATIMENT'),(10,'TVX NEUFS','Service créé depuis le fichier Excel: TVX NEUFS'),(11,'CENTRALE  ELECTRIQUE','Service créé depuis le fichier Excel: CENTRALE  ELECTRIQUE'),(12,'TRANSPORT','Service créé depuis le fichier Excel: TRANSPORT'),(13,'SCE METHODE','Service créé depuis le fichier Excel: SCE METHODE'),(14,'CONST MECANIQUE','Service créé depuis le fichier Excel: CONST MECANIQUE'),(15,'WIRE LINE','Service créé depuis le fichier Excel: WIRE LINE'),(16,'SECURITE','Service créé depuis le fichier Excel: SECURITE'),(17,'INSTRUMENTATION','Service créé depuis le fichier Excel: INSTRUMENTATION'),(18,'MACHINE TOURNANTE','Service créé depuis le fichier Excel: MACHINE TOURNANTE'),(19,'LIGNE AERIENNE','Service créé depuis le fichier Excel: LIGNE AERIENNE'),(20,'PROJET AGRICOLE','Service créé depuis le fichier Excel: PROJET AGRICOLE'),(21,'ENTRETIEN CHAMP','Service créé depuis le fichier Excel: ENTRETIEN CHAMP'),(22,'MAGASIN','Service créé depuis le fichier Excel: MAGASIN'),(23,'GARAGE MECANIQUE','Service créé depuis le fichier Excel: GARAGE MECANIQUE'),(24,'STEG CENTRALE','Service créé depuis le fichier Excel: STEG CENTRALE'),(25,'TSP','Service créé depuis le fichier Excel: TSP'),(26,'GARRAGE','Service créé depuis le fichier Excel: GARRAGE'),(27,'BASE','Service créé depuis le fichier Excel: BASE'),(28,'G.CIVIL','Service créé depuis le fichier Excel: G.CIVIL '),(29,'DIV MAINTENANCE','Service créé depuis le fichier Excel: DIV MAINTENANCE'),(30,'DIV PRODUCTION','Service créé depuis le fichier Excel: DIV PRODUCTION '),(31,'BANC D\'ESSAI','Service créé depuis le fichier Excel: BANC D\'ESSAI');
/*!40000 ALTER TABLE `service` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suivi_dossier`
--

DROP TABLE IF EXISTS `suivi_dossier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suivi_dossier` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `numero_com` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dat_com` date NOT NULL,
  `code_fourn` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_etape` smallint unsigned NOT NULL,
  `influence_sur_dossier` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `libelle_etape` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_etape` date NOT NULL,
  `numero_bordereau` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `numero_avis` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `numero_ci` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `numero_facture` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_facture` date DEFAULT NULL,
  `numero_bl` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_bl` date DEFAULT NULL,
  `observation` longtext COLLATE utf8mb4_unicode_ci,
  `email_data` json DEFAULT NULL,
  `date_avis` date DEFAULT NULL,
  `bct` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_bct` date DEFAULT NULL,
  `date_bordereau` date DEFAULT NULL,
  `date_email` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `suivi_dossi_numero__9b1ab1_idx` (`numero_com`,`dat_com`,`code_fourn`),
  KEY `suivi_dossi_id_etap_e383e6_idx` (`id_etape`),
  CONSTRAINT `suivi_dossier_chk_1` CHECK ((`id_etape` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=111 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suivi_dossier`
--

LOCK TABLES `suivi_dossier` WRITE;
/*!40000 ALTER TABLE `suivi_dossier` DISABLE KEYS */;
INSERT INTO `suivi_dossier` VALUES (101,'0176/2025L','2025-07-31','1223',1,'autre','Etablissement BC / Contrat','2025-10-31',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'aaaa',NULL,NULL,NULL,NULL,NULL,NULL),(103,'0176/2025L','2025-07-31','1223',3,'instance','Reception Materiel au Magasin EBC','2025-10-31','10/2025','','','',NULL,'',NULL,'zzz',NULL,NULL,NULL,NULL,NULL,NULL),(105,'0176/2025L','2025-08-01','1223',4,'instance','Etablissement Avis d\'arrivée - Email','2025-11-02','','2810','','',NULL,'',NULL,'','{\"corps\": \"Réception de l’ambulance\\r\\nAymen Cherni\\r\\nven. 31/10, 10:40\\r\\nImededdine ElMekki;\\r\\nkarim Ben Halima;\\r\\nNebil Ben aissa;\\r\\nJawhar Karoui\\r\\nL\'expéditeur du message a demandé une confirmation de lecture. Pour envoyer une confirmation, cliquez ici.\\r\\n2 pièce(s) jointe(s) (353 Ko) Télécharger tout \\r\\nBonjour,\\r\\n \\r\\nSuite à votre demande, veuillez trouver ci-joint la facture ainsi que la liste de colisage, pour suite utile.\\r\\n \\r\\nSalutations .\\r\\n\\r\\n\\r\\nImededdine ElMekki\\r\\nven. 31/10, 10:04\\r\\nBonjour, PVI. Si vous avez des copies de ces documents (Facture , liste de colisage) , merci de bien vouloir nous les transmettre. SD.\\r\\n\\r\\nImededdine ElMekki\\r\\njeu. 30/10, 11:25\\r\\nBonjour, Nous vous informons que l’ambulance a été réceptionnée. À ce jour, nous sommes toujours en attente des documents nécessaires à la finalisation de cette livraison, à savoir : Le procès-verbal de la reception (PV) La facture La liste de colisage détaillée.\\r\\n\", \"date_import\": \"2025-11-05T10:04:16.999998+00:00\"}',NULL,'',NULL,NULL,NULL),(106,'0176/2025L','2025-08-01','1223',4,'instance','Etablissement Avis d\'arrivée - Email','2025-11-01','','','','',NULL,'',NULL,'','{\"corps\": \"\", \"date_import\": \"2025-11-01T06:42:53.743313+00:00\"}',NULL,NULL,NULL,NULL,NULL),(108,'0155/2023L','2023-09-22','0974',3,'instance','Reception Materiel au Magasin EBC','2025-11-01','','','','',NULL,'',NULL,'','{\"corps\": \"Besoin d\'information : audit inventaire 2023- questionnement pour chaque point:\\r\\nTarek Sedki\\r\\nsam. 01/11/2025 08:58\\r\\nRiadh Snoussi;\\r\\nMeriem Hallaja\\r\\nImededdine ElMekki;\\r\\nmiloud messaoudi;\\r\\nIsmail Nfis;\\r\\nRidha Mansali\\r\\n2 pièce(s) jointe(s) (1 Mo) Télécharger tout \\r\\nBonjour,\\r\\n\\r\\nNous vous informons que le responsable magasin EBC pendant la période d\'inventaire pour les deux tranches année 2023 est Mr Sami ZORGATI téléphone : 98 403 257.\\r\\nNB : Mr Sami ZORGATI est en retraite depuis 05 Novembre 2024.\\r\\n\\r\\nMM.  Miloud MASSOUDI et Imeddine ELMEKKI sont appelés en coordination avec les unités concernées à préparer les autres éléments de réponse point au cours de la semaine prochaine.  \\r\\n\\r\\nContacts:\\r\\nImeddine ELMEKKI : 93 242 069\\r\\nMiloud MASSOUDI : 98 555 097\\r\\n\\r\\nNous sommes à votre disposition pour tout complément d\'information.\\r\\n\\r\\nSalutations\\r\\nTarek SEDKI\\r\\nDe : Riadh Snoussi\\r\\nEnvoyé : lundi 20 octobre 2025 16:42\\r\\nÀ : Najmeddine Sabri; Wajdi Ben Salem; karim Ben Halima; Tarek Sedki\\r\\nCc : Hazem Yahiaoui; Mustapha Loussaief; Meriem Hallaja\\r\\nObjet : Besoin d\'information : audit inventaire 2023- questionnement pour chaque point:\\r\\n \\r\\nBon après-midi,\\r\\n \\r\\nPièce Jointe :     -Ordre de mission.\\r\\n-Note DG.\\r\\n \\r\\nNous vous prions de nous communiquer ce qui suit :\\r\\n \\r\\nPersonnes à contacter :\\r\\n-Le nom du responsable magasin EBC et son numéro de téléphone, pendant le période d’inventaire pour les deux tranches année 2023.\\r\\n-le nom du chargé d’inventaire par la Direction Financière pour l’année 2023.\\r\\n-le nom du chargé de la direction initiatrice participant à l’inventaire de l’année 2023.\\r\\n \\r\\nManuel de procédure d’inventaire physique :\\r\\n-le manuel de procédure d’inventaire en vigueur du matériel consommable.\\r\\n \\r\\nDocuments à fournir :\\r\\n-l’emplacement de chaque article (cité à la note DG en pièce jointe) au magasin ainsi son code (muni d’une photo ou plusieurs) et son poids approximatif.\\r\\n-état d’inventaire des années précédentes pour ces 04 articles.\\r\\n-l’état des écarts résultants des années antérieures pour ces 04 articles.\\r\\n \\r\\nQuestions :\\r\\n-A quoi servent ces articles manquants : on a besoin d’un descriptif technique (svp par article) ?\\r\\n-L’éventuel utilisation de ces articles manquants, est-elle imminente pour le chantier ? \\r\\n-L’état de ces articles : neufs, moyennement neufs, très ancien.\\r\\n-Le risque d’un stock nul pour ces 4 articles.\\r\\n-La manutention de ces articles est simple, moyen ou lourde.\\r\\n-L’accès à ces articles est facile, moyen ou sécurisé.\\r\\n-Leur valeur réel en ce moment pour chaque article.\\r\\n-Quels sont d’après vous, les mesures correctrices pour que cet évènement ne sera pas récidive afin de minimiser \", \"date_import\": \"2025-11-01T09:36:21.125887+00:00\"}',NULL,NULL,NULL,NULL,NULL),(109,'0013/2024E','2024-09-17','0933',3,'instance','Reception Materiel au Magasin EBC','2025-11-04','','','','',NULL,'',NULL,'','{\"corps\": \"\", \"date_import\": \"2025-11-04T09:11:30.726273+00:00\"}',NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `suivi_dossier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tache`
--

DROP TABLE IF EXISTS `tache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tache` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `libelle` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_prevue` date NOT NULL,
  `observation` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `delai_repetition` int unsigned NOT NULL,
  `etat` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `planning_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tache_planning_id_d13aab34_fk_planning_tache_id` (`planning_id`),
  CONSTRAINT `tache_planning_id_d13aab34_fk_planning_tache_id` FOREIGN KEY (`planning_id`) REFERENCES `planning_tache` (`id`),
  CONSTRAINT `tache_chk_1` CHECK ((`delai_repetition` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tache`
--

LOCK TABLES `tache` WRITE;
/*!40000 ALTER TABLE `tache` DISABLE KEYS */;
INSERT INTO `tache` VALUES (1,'ِControle Parc Tube Desenssablement Si necessaire','','2025-12-01','',30,'a_faire','2025-11-08 06:54:52.965665','2025-11-08 07:43:00.629258',NULL),(2,'Controle de articles ayant un date Peremption','','2026-01-01','',0,'a_faire','2025-11-08 07:13:54.914080','2025-11-10 06:53:56.069928',NULL);
/*!40000 ALTER TABLE `tache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tiers`
--

DROP TABLE IF EXISTS `tiers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tiers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code_tiers` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `raison_sociale` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telephone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type_tiers` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `actif` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_tiers` (`code_tiers`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tiers`
--

LOCK TABLES `tiers` WRITE;
/*!40000 ALTER TABLE `tiers` DISABLE KEYS */;
INSERT INTO `tiers` VALUES (1,'01','Ben Kilani','','','','prestataire',1);
/*!40000 ALTER TABLE `tiers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `type_mouvement`
--

DROP TABLE IF EXISTS `type_mouvement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `type_mouvement` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `libelle` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci,
  `sens` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `actif` tinyint(1) NOT NULL,
  `date_creation` datetime(6) NOT NULL,
  `date_modification` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `type_mouvement`
--

LOCK TABLES `type_mouvement` WRITE;
/*!40000 ALTER TABLE `type_mouvement` DISABLE KEYS */;
INSERT INTO `type_mouvement` VALUES (1,'1','Entree Stock','','entree',1,'2025-09-15 13:50:26.483756','2025-09-15 13:50:26.483787'),(2,'2','Sortie Stock','','sortie',1,'2025-09-15 13:50:55.921351','2025-09-15 13:50:55.921372'),(3,'3','Changement Emplacement','','neutre',1,'2025-09-15 13:51:54.077483','2025-09-15 13:51:54.077501');
/*!40000 ALTER TABLE `type_mouvement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `valeur_article`
--

DROP TABLE IF EXISTS `valeur_article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `valeur_article` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code_valeur` smallint unsigned NOT NULL,
  `libelle_valeur` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_valeur` (`code_valeur`),
  CONSTRAINT `valeur_article_chk_1` CHECK ((`code_valeur` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `valeur_article`
--

LOCK TABLES `valeur_article` WRITE;
/*!40000 ALTER TABLE `valeur_article` DISABLE KEYS */;
INSERT INTO `valeur_article` VALUES (1,1,'100%'),(2,2,'75%'),(3,3,'25%'),(4,4,'0%');
/*!40000 ALTER TABLE `valeur_article` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-10 16:49:21
