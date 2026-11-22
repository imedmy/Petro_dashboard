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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_customuser`
--

LOCK TABLES `accounts_customuser` WRITE;
/*!40000 ALTER TABLE `accounts_customuser` DISABLE KEYS */;
INSERT INTO `accounts_customuser` VALUES (1,'pbkdf2_sha256$1000000$ZAlLSEMBSvpF0Ga8EQQbGo$MPSm0OewScXuZNCaCzUFQJxMQG/BSrU/eebOX0CubZs=','2025-10-12 10:09:58.408159',1,'sitep','','','imedmy@gmail.com',1,1,'2025-08-13 08:51:36.984771','93242069','None','2025-08-13 08:51:37.500012','2025-08-15 08:06:56.881256'),(2,'pbkdf2_sha256$600000$HqwyruVCddC08cKQU5rzyA$6D82GNok/JYWGdaC9fUdBOKNLte/z8XbZCGOj2HaD60=',NULL,0,'imed','Imed Eddine','ellmekki','imedmy@gmail.com',1,1,'2025-08-15 09:10:34.349563','93242069','','2025-08-15 09:10:34.851785','2025-09-03 09:22:16.635989');
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
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add مستخدم',6,'add_customuser'),(22,'Can change مستخدم',6,'change_customuser'),(23,'Can delete مستخدم',6,'delete_customuser'),(24,'Can view مستخدم',6,'view_customuser'),(25,'Can add معلومات الشركة',7,'add_companyinfo'),(26,'Can change معلومات الشركة',7,'change_companyinfo'),(27,'Can delete معلومات الشركة',7,'delete_companyinfo'),(28,'Can view معلومات الشركة',7,'view_companyinfo'),(29,'Can add صفحة',8,'add_page'),(30,'Can change صفحة',8,'change_page'),(31,'Can delete صفحة',8,'delete_page'),(32,'Can view صفحة',8,'view_page'),(33,'Can add مصفوفة الصلاحيات',9,'add_permissionmatrix'),(34,'Can change مصفوفة الصلاحيات',9,'change_permissionmatrix'),(35,'Can delete مصفوفة الصلاحيات',9,'delete_permissionmatrix'),(36,'Can view مصفوفة الصلاحيات',9,'view_permissionmatrix'),(37,'Can add article',10,'add_article'),(38,'Can change article',10,'change_article'),(39,'Can delete article',10,'delete_article'),(40,'Can view article',10,'view_article'),(41,'Can add Famille d\'article',11,'add_articlefamily'),(42,'Can change Famille d\'article',11,'change_articlefamily'),(43,'Can delete Famille d\'article',11,'delete_articlefamily'),(44,'Can view Famille d\'article',11,'view_articlefamily'),(45,'Can add article sql',12,'add_articlesql'),(46,'Can change article sql',12,'change_articlesql'),(47,'Can delete article sql',12,'delete_articlesql'),(48,'Can view article sql',12,'view_articlesql'),(49,'Can add Caractéristique',13,'add_caracteristique'),(50,'Can change Caractéristique',13,'change_caracteristique'),(51,'Can delete Caractéristique',13,'delete_caracteristique'),(52,'Can view Caractéristique',13,'view_caracteristique'),(53,'Can add Image Article',14,'add_articleimage'),(54,'Can change Image Article',14,'change_articleimage'),(55,'Can delete Image Article',14,'delete_articleimage'),(56,'Can view Image Article',14,'view_articleimage'),(57,'Can add Valeur Caractéristique Article',15,'add_articlecaracteristique'),(58,'Can change Valeur Caractéristique Article',15,'change_articlecaracteristique'),(59,'Can delete Valeur Caractéristique Article',15,'delete_articlecaracteristique'),(60,'Can view Valeur Caractéristique Article',15,'view_articlecaracteristique'),(61,'Can add Unité avec Numéro de Série',16,'add_serialunit'),(62,'Can change Unité avec Numéro de Série',16,'change_serialunit'),(63,'Can delete Unité avec Numéro de Série',16,'delete_serialunit'),(64,'Can view Unité avec Numéro de Série',16,'view_serialunit'),(65,'Can add Type de Mouvement',17,'add_typemouvement'),(66,'Can change Type de Mouvement',17,'change_typemouvement'),(67,'Can delete Type de Mouvement',17,'delete_typemouvement'),(68,'Can view Type de Mouvement',17,'view_typemouvement'),(69,'Can add Nature de stock',18,'add_naturestock'),(70,'Can change Nature de stock',18,'change_naturestock'),(71,'Can delete Nature de stock',18,'delete_naturestock'),(72,'Can view Nature de stock',18,'view_naturestock'),(73,'Can add Valeur d\'article',19,'add_valeurarticle'),(74,'Can change Valeur d\'article',19,'change_valeurarticle'),(75,'Can delete Valeur d\'article',19,'delete_valeurarticle'),(76,'Can view Valeur d\'article',19,'view_valeurarticle'),(77,'Can add Étape de dossier',20,'add_etapedossier'),(78,'Can change Étape de dossier',20,'change_etapedossier'),(79,'Can delete Étape de dossier',20,'delete_etapedossier'),(80,'Can view Étape de dossier',20,'view_etapedossier');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_articlecaracteristique`
--

LOCK TABLES `core_articlecaracteristique` WRITE;
/*!40000 ALTER TABLE `core_articlecaracteristique` DISABLE KEYS */;
INSERT INTO `core_articlecaracteristique` VALUES (2,'000000000A','10',71),(3,'581200078Q','10',99),(5,'000000000A','10',40),(6,'416720490E','oui',129),(7,'774000001Z','165/70/14',1),(8,'000000000A','10',22);
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
) ENGINE=InnoDB AUTO_INCREMENT=131 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_caracteristique`
--

LOCK TABLES `core_caracteristique` WRITE;
/*!40000 ALTER TABLE `core_caracteristique` DISABLE KEYS */;
INSERT INTO `core_caracteristique` VALUES (1,'Dimensions & Forme','text','',1,NULL),(2,'Matière & Composition','text','',1,NULL),(3,'Pression & Température','text','',1,NULL),(4,'Électrique','text','',1,NULL),(5,'Mécanique','text','',1,NULL),(6,'Hydraulique & Pneumatique','text','',1,NULL),(7,'Connectique & Raccordement','text',NULL,1,NULL),(8,'Identification & Traçabilité','text','',1,NULL),(9,'Performance & Durée','text','',1,NULL),(10,'Sécurité','text','',1,NULL),(11,'Environnement','text','',1,NULL),(12,'Outillage & Maintenance','text','',1,NULL),(13,'Spécifique à l\'application','text','',1,NULL),(14,'Diamètre nominal','unit','mm',1,1),(15,'Diamètre extérieur','unit','mm',1,1),(16,'Diamètre intérieur','unit','mm',1,1),(17,'Épaisseur de paroi','unit','mm',1,1),(18,'Longueur','unit','m',1,1),(19,'Largeur','unit','mm',1,1),(20,'Hauteur','unit','mm',1,1),(21,'Poids','unit','kg',1,1),(22,'Volume','unit','m³',1,1),(23,'Section','unit','cm²',1,1),(24,'Rayon de courbure','unit','mm',1,1),(25,'Matériau principal','choice','',1,2),(26,'Revêtement','text','',1,2),(27,'Densité','unit','g/cm³',1,2),(28,'Résistance à la traction','unit','MPa',1,2),(29,'Limite élastique','unit','MPa',1,2),(30,'Type de plastique','choice','',1,2),(31,'Teneur en carbone','number','%',1,2),(32,'Dureté (Rockwell)','number','',1,2),(33,'Pression nominale','unit','bar',1,3),(34,'Pression max','unit','bar',1,3),(35,'Pression min','unit','bar',1,3),(36,'Température nominale','unit','°C',1,3),(37,'Température max','unit','°C',1,3),(38,'Température min','unit','°C',1,3),(39,'Température de fonctionnement','text','°C',1,3),(40,'Classe de pression','text','PN',1,3),(41,'Pression nominale','unit','bar',1,3),(42,'Pression max','unit','bar',1,3),(43,'Pression min','unit','bar',1,3),(44,'Température nominale','unit','°C',1,3),(45,'Température max','unit','°C',1,3),(46,'Température min','unit','°C',1,3),(47,'Température de fonctionnement','text','°C',1,3),(48,'Classe de pression','text','PN',1,3),(49,'Tension nominale','unit','V',1,4),(50,'Tension d\'isolation','unit','V',1,4),(51,'Intensité nominale','unit','A',1,4),(52,'Puissance électrique','unit','kW',1,4),(53,'Puissance hydraulique','unit','HP',1,4),(54,'Fréquence','unit','Hz',1,4),(55,'Facteur de puissance','number','',1,4),(56,'Degré de protection','text','IP',1,4),(57,'Type de courant','choice','',1,4),(58,'Nombre de pôles','number','',1,4),(59,'Capacité de démarrage','unit','kVA',1,4),(60,'Vitesse nominale','unit','tr/min',1,5),(61,'Vitesse max','unit','tr/min',1,5),(62,'Couple nominal','unit','Nm',1,5),(63,'Type de transmission','choice','',1,5),(64,'Type de joint','choice','',1,5),(65,'Type de filetage','text','',1,5),(66,'Pas de filetage','unit','mm',1,5),(67,'Diamètre de filetage','unit','mm',1,5),(68,'Type de roulement','text','',1,5),(69,'Jeu mécanique','unit','mm',1,5),(70,'Débit nominal','unit','l/min',1,6),(71,'Débit max','unit','l/min',1,6),(72,'Pression hydraulique','unit','bar',1,6),(73,'Type de fluide','choice','',1,6),(74,'Viscosité','unit','cSt',1,6),(75,'Filtre intégré','boolean','',1,6),(76,'Type de raccord','choice','',1,7),(77,'Norme des raccordement','text',NULL,1,7),(78,'Nombre de voies','number',NULL,1,7),(79,'Type de prise','text','',1,7),(80,'Type de fiche','text','',1,7),(81,'Section du câble','unit','mm²',1,7),(82,'Type de connecteur','text','',1,7),(83,'Type de raccord','choice','',1,7),(84,'Norme de raccordement','text','',1,7),(85,'Nombre des voies','number',NULL,1,NULL),(86,'Type de prise','text','',1,7),(87,'Type de fiche','text','',1,7),(88,'Section du câble','unit','mm²',1,7),(89,'Type de connecteur','text','',1,7),(90,'Rendement','number','%',1,9),(91,'Durée de vie','unit','heures',1,9),(92,'Durée de garantie','unit','mois',1,9),(93,'Précision','number','%',1,9),(94,'Fréquence de maintenance','unit','heures',1,9),(95,'Cycle de vie','number','',1,9),(96,'Charge maximale','unit','t',1,10),(97,'Charge de rupture','unit','t',1,10),(98,'Norme de sécurité','text','',1,10),(99,'Classe de risque','choice','',1,10),(100,'Certification','text','',1,10),(101,'Protection contre les surtensions','boolean','',1,10),(102,'Température ambiante','text','°C',1,11),(103,'Humidité relative max','number','%',1,11),(104,'Résistance aux UV','boolean','',1,11),(105,'Indice de protection','text','IP',1,11),(106,'Résistance aux chocs','text','IK',1,11),(107,'Outil de montage','text','',1,12),(108,'Outil de démontage','text','',1,12),(109,'Couple de serrage','unit','Nm',1,12),(110,'Type de clé','text','',1,12),(111,'Lubrifiant recommandé','text','',1,12),(112,'Fréquence de graissage','unit','heures',1,12),(113,'Application','choice','',1,13),(114,'Type d\'appareil','text','',1,13),(115,'Classe de forage','text','',1,13),(116,'Type de turbine','choice','',1,13),(117,'Type de vanne','choice','',1,13),(118,'Type de pompe','choice','',1,13),(119,'Type de moteur','choice','',1,13),(120,'Type de filtre','choice','',1,13),(121,'Shedule','choice','',1,13),(122,'Norme (API, ASME, DIN)','text','',1,13),(123,'Vanne papillon','text','',0,117),(124,'Vanne bille','text','',0,117),(125,'Vanne à guillotine','text','',0,117),(126,'Forage','text','',0,113),(127,'Turbine à gaz','text','',0,113),(128,'Laboratoire','text','',0,113),(129,'Identifié par numéro de série','boolean',NULL,1,NULL),(130,'Has a Serial Number','boolean',NULL,1,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_permissionmatrix`
--

LOCK TABLES `core_permissionmatrix` WRITE;
/*!40000 ALTER TABLE `core_permissionmatrix` DISABLE KEYS */;
INSERT INTO `core_permissionmatrix` VALUES (1,1,1,1,1,'2025-08-14 09:40:45.611419','2025-08-16 09:18:43.443654',1,1),(2,1,1,1,1,'2025-08-14 09:40:45.661308','2025-08-16 09:19:52.621643',2,1),(3,1,1,1,1,'2025-08-14 09:40:45.752065','2025-08-14 09:40:45.752134',3,1),(4,1,1,1,1,'2025-08-14 09:40:45.802651','2025-08-14 09:40:45.802719',4,1),(6,1,1,1,1,'2025-08-16 09:20:04.892040','2025-08-16 09:20:04.892059',5,1),(7,1,1,1,1,'2025-09-03 16:13:41.482510','2025-09-03 16:14:27.846901',6,1),(8,1,1,1,1,'2025-09-11 10:35:38.307733','2025-09-12 06:32:59.205744',7,1);
/*!40000 ALTER TABLE `core_permissionmatrix` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (6,'accounts','customuser'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(10,'core','article'),(15,'core','articlecaracteristique'),(11,'core','articlefamily'),(14,'core','articleimage'),(12,'core','articlesql'),(13,'core','caracteristique'),(7,'core','companyinfo'),(20,'core','etapedossier'),(18,'core','naturestock'),(8,'core','page'),(9,'core','permissionmatrix'),(16,'core','serialunit'),(17,'core','typemouvement'),(19,'core','valeurarticle'),(5,'sessions','session');
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
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-08-13 08:50:27.889920'),(2,'contenttypes','0002_remove_content_type_name','2025-08-13 08:50:30.110924'),(3,'auth','0001_initial','2025-08-13 08:50:33.598341'),(4,'auth','0002_alter_permission_name_max_length','2025-08-13 08:50:34.697711'),(5,'auth','0003_alter_user_email_max_length','2025-08-13 08:50:34.736887'),(6,'auth','0004_alter_user_username_opts','2025-08-13 08:50:34.778511'),(7,'auth','0005_alter_user_last_login_null','2025-08-13 08:50:34.841816'),(8,'auth','0006_require_contenttypes_0002','2025-08-13 08:50:34.897654'),(9,'auth','0007_alter_validators_add_error_messages','2025-08-13 08:50:34.965611'),(10,'auth','0008_alter_user_username_max_length','2025-08-13 08:50:35.032529'),(11,'auth','0009_alter_user_last_name_max_length','2025-08-13 08:50:35.092413'),(12,'auth','0010_alter_group_name_max_length','2025-08-13 08:50:35.236468'),(13,'auth','0011_update_proxy_permissions','2025-08-13 08:50:35.299991'),(14,'auth','0012_alter_user_first_name_max_length','2025-08-13 08:50:35.365548'),(15,'accounts','0001_initial','2025-08-13 08:50:40.177129'),(16,'admin','0001_initial','2025-08-13 08:50:42.378690'),(17,'admin','0002_logentry_remove_auto_add','2025-08-13 08:50:42.419513'),(18,'admin','0003_logentry_add_action_flag_choices','2025-08-13 08:50:42.528761'),(19,'sessions','0001_initial','2025-08-13 08:50:43.192558'),(20,'core','0001_initial','2025-08-14 07:45:29.362059'),(21,'core','0002_article_articlefamily','2025-09-05 09:58:41.694104'),(22,'core','0003_alter_articlefamily_options_and_more','2025-09-05 15:20:20.219016'),(23,'core','0004_remove_articlefamily_created_at_and_more','2025-09-05 15:29:22.234426'),(24,'core','0005_alter_articlefamily_options_articlefamily_full_code','2025-09-06 06:55:48.775074'),(25,'core','0006_articlesql_caracteristique','2025-09-07 10:24:11.932406'),(26,'core','0007_alter_caracteristique_nom','2025-09-08 10:44:25.919927'),(27,'core','0008_alter_caracteristique_options_and_more','2025-09-08 10:44:32.593494'),(28,'core','0009_caracteristique_parent_and_more','2025-09-09 06:24:31.988269'),(29,'core','0010_articleimage_articlecaracteristique','2025-09-10 15:40:11.203402'),(30,'core','0011_serialunit_delete_article_alter_articleimage_image_and_more','2025-09-15 09:58:34.700235'),(31,'core','0012_typemouvement','2025-09-15 10:06:42.322153'),(32,'core','0013_naturestock','2025-10-07 06:54:16.758023'),(33,'core','0014_valeurarticle','2025-10-07 08:50:04.799399'),(34,'core','0015_etapedossier','2025-10-07 09:11:23.760552'),(35,'core','0016_etapedossier_influence','2025-10-07 09:32:44.752502');
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
INSERT INTO `django_session` VALUES ('0wdx6ai829zbvb1lx3qg6bg4xlsgdc9g','.eJxVjMsOwiAUBf-FtSE8hbh07zcQ7gOpGkhKu2r8d23ShW7PzJxNpLwuNa2D5zSRuAgtTr8bZHxy2wE9crt3ib0t8wRyV-RBh7x14tf1cP8Oah71W1t0hQwYVM5qrzAihAAl5EIQwZIxGJ33wCUGzdHCGYxDtMCsXFBKvD_9yzh8:1unBJV:VryrdZKxYPamU_v5uiR7rIWWI2R09l73l4iIrgxuOOU','2025-08-30 07:26:53.713049'),('4bhniwes9n6cp2jli4lvxk0o1z9kb9up','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v3qKa:O7lWY3qBuqBhzEOAP1RL8s-r5pwRUaEjLdDWXIk3tNo','2025-10-15 06:28:52.898575'),('6k0dfmb5l7m7ak1w5jr0v0z95m0lbbe9','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uwybg:uJ01m5OqlUa2kVatlIehEimQNUhiXEvN6-f2B2ifyrs','2025-09-26 07:54:08.681487'),('6k0ez2fv2sdw5hvo2rk5or9gt9gfiyfx','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uwEcx:aLFNQT8EXMgUmnIEi6UvKbYSx-9t9GEd8yLpCD1_xQ4','2025-09-24 06:48:23.921826'),('7x7u7ar30wmshcw5oam6gxwt6x8zd8ye','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v6V9y:j4GQfi5sv_bUhmicmA4PdTD1UvAGVUWmjxHUuY8SEgc','2025-10-22 14:28:54.046908'),('f2vlge53u12uj803dksouana0hm12wur','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v6Q9b:nkIRs4K99ph9vmoqrHVRmgAEokaXjhMcII2c1r92Qqw','2025-10-22 09:08:11.321789'),('itery4n6lir7m15b151054znkjkyu652','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v6ULS:25AkssfYLcjVNrU4Gsy3hAv6uzaM_XXP1lqKPoj8PFU','2025-10-22 13:36:42.450003'),('jfveot7ic3pd6dyddwlzvfkhqkatzurq','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v7t1a:OHkTImzrfF6TtFBgzI5iJwMFMDNW3QzdrIKmLFM-3Gc','2025-10-26 10:09:58.551711'),('ki8p3uhmyywbtnp8szyte0jhsvqgy47z','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v4yUt:oZNgD8-H4Ht38-nEpPmtKOy34JBqG748nFnj_Z7SN70','2025-10-18 09:24:11.826380'),('kk72t6f9upxtywpxmqtvkgpddvukj04f','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uvujb:HntjRgEPw1CcAKJ8JhMnwiNIl2r3e-SIUtZpbZO74uk','2025-09-23 09:33:55.836459'),('krn1cy99jcsx6wspwa5yugulqkp0aiog','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uvuWT:BqsB6t6cZBKfpAeeVtVGRSSRlnIJoF3Cr4-ORLmfdJs','2025-09-23 09:20:21.296807'),('oucp4znkbeu4w60b6tfn3dbha76b57hg','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uwHH1:KVJMjeo1Ws65z194TL9sBO5A3_13wNbHXXxR0bR1XBk','2025-09-24 09:37:55.433520'),('qcfkua4dgqsezclv5gwjsb7p7hi3uc40','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v6OcD:5crdIqb_gY_iCAKYMKm5fNFWohRppdLGHZscyzpO0pQ','2025-10-22 07:29:37.635797'),('su65qionnkny66dj4x2yfiyhn4rqoedm','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v63kg:R4wD-Cd5OpH66XyY925w8MpoOs679KCRg5o1qVsnWXM','2025-10-21 09:12:58.009926'),('vfn91apd0l5qfhf8i2k58d1jid83e93e','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v7WxS:RRFiGK-UwK5Lv1JE0xE4EVUGSLAzFIC23brBSJEwfI8','2025-10-25 10:36:14.906716'),('wmphrb1j08tdv4u9bmk6kgdouq5m64n9','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v4K3S:SxDheCLj2rFfSp_VSTsRHSfmxGyxdSpzIU0gHaNBvJ0','2025-10-16 14:13:10.746885'),('xepbjcl2sdy9wz9lrh4zf9lwq5fftd2z','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1v68bB:Wf2ivj9qMj1WNuAXItTbLojvwaKRdgeCc7tseKlyZBM','2025-10-21 14:23:29.187443'),('xzsorzpw2fwtwu6hfe5d3xxp9srigglw','.eJxVjLEOwjAQQ_8lM4oamnAtI3u_IbrL5UgBJVLTToh_J5U6wODBfrbfyuO2Jr_VuPiZ1VUZdfrNCMMz5h3wA_O96FDyusyk94o-aNVT4fi6Hd2_g4Q1tXVn4yACdBmxBydMoxghcyaMlvoBIogDtA44gG1C12wnDpkAkER9vgmCOTQ:1uyS26:2c8Nkqou4LsyW2bdOJoHCIXONwR6-074alIwABub-_c','2025-09-30 09:31:30.451241');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etape_dossier`
--

LOCK TABLES `etape_dossier` WRITE;
/*!40000 ALTER TABLE `etape_dossier` DISABLE KEYS */;
INSERT INTO `etape_dossier` VALUES (1,1,'Etablissement BC / Contrat','autre'),(2,2,'Reception Materiel au Magasin Tunis','instance'),(3,3,'Reception Materiel au Magasin EBC','instance'),(4,4,'Etablissement Avis d\'arrivée - Email','instance'),(5,5,'Reception Partiel','instance'),(6,6,'Reception Partiel B1 Etablie','instance'),(7,7,'Reception Total','instance'),(8,8,'Reception Total B1 Etablie','cloture');
/*!40000 ALTER TABLE `etape_dossier` ENABLE KEYS */;
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

-- Dump completed on 2025-10-13 16:30:46
