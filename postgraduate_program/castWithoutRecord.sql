/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 50725
 Source Host           : localhost:3306
 Source Schema         : cast

 Target Server Type    : MySQL
 Target Server Version : 50725
 File Encoding         : 65001

 Date: 06/11/2019 13:12:45
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for emc_data
-- ----------------------------
DROP TABLE IF EXISTS `emc_data`;
CREATE TABLE `emc_data`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `band_width` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `center_freq` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `create_time` bigint(20) NULL DEFAULT NULL,
  `data` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `device` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `item` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `modulation` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `place` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `remarks` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `snr` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `report` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `interference_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 32 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for envir_data
-- ----------------------------
DROP TABLE IF EXISTS `envir_data`;
CREATE TABLE `envir_data`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` bigint(20) NULL DEFAULT NULL,
  `data` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `envelope` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `exceed` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `frequencyl` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `frequencyr` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `item` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `layout` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `place` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `pol` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `report` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `standard` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `state` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for freq_data
-- ----------------------------
DROP TABLE IF EXISTS `freq_data`;
CREATE TABLE `freq_data`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` bigint(20) NULL DEFAULT NULL,
  `data` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `item` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `modulation` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `place` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `remarks` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `device` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `frequencyl` decimal(19, 2) NULL DEFAULT NULL,
  `frequencyr` decimal(19, 2) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for label
-- ----------------------------
DROP TABLE IF EXISTS `label`;
CREATE TABLE `label`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `content` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for operation
-- ----------------------------
DROP TABLE IF EXISTS `operation`;
CREATE TABLE `operation`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `operation_content` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `operation_data_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `operation_ip` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `operation_time` bigint(20) NULL DEFAULT NULL,
  `operation_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for pulse_data
-- ----------------------------
DROP TABLE IF EXISTS `pulse_data`;
CREATE TABLE `pulse_data`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` bigint(20) NULL DEFAULT NULL,
  `data` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `device` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `item` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `place` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `remarks` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 30 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sample_data
-- ----------------------------
DROP TABLE IF EXISTS `sample_data`;
CREATE TABLE `sample_data`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` bigint(20) NULL DEFAULT NULL,
  `data` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `signal_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 42 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sample_data
-- ----------------------------
INSERT INTO `sample_data` VALUES (1, NULL, '/file/sample_data/fan.txt', 'TIME', 'fan');
INSERT INTO `sample_data` VALUES (2, NULL, '/file/sample_data/power.txt', 'TIME', 'power');
INSERT INTO `sample_data` VALUES (3, NULL, '/file/sample_data/WD_200.txt', 'TIME', 'wd200');
INSERT INTO `sample_data` VALUES (4, NULL, '/file/sample_data/shipeiqi.txt', 'TIME', 'shipeiqi');
INSERT INTO `sample_data` VALUES (5, NULL, '/file/sample_data/GSM900_0.txt', 'FREQUENCY', 'GSM900');
INSERT INTO `sample_data` VALUES (6, NULL, '/file/sample_data/GSM900_1.txt', 'FREQUENCY', 'GSM900');
INSERT INTO `sample_data` VALUES (7, NULL, '/file/sample_data/GSM900_2.txt', 'FREQUENCY', 'GSM900');
INSERT INTO `sample_data` VALUES (8, NULL, '/file/sample_data/GSM900_3.txt', 'FREQUENCY', 'GSM900');
INSERT INTO `sample_data` VALUES (9, NULL, '/file/sample_data/GSM900_4.txt', 'FREQUENCY', 'GSM900');
INSERT INTO `sample_data` VALUES (10, NULL, '/file/sample_data/GSM900_5.txt', 'FREQUENCY', 'GSM900');
INSERT INTO `sample_data` VALUES (11, NULL, '/file/sample_data/WCDMA_0.txt', 'FREQUENCY', 'WCDMA');
INSERT INTO `sample_data` VALUES (12, NULL, '/file/sample_data/WCDMA_1.txt', 'FREQUENCY', 'WCDMA');
INSERT INTO `sample_data` VALUES (13, NULL, '/file/sample_data/WCDMA_2.txt', 'FREQUENCY', 'WCDMA');
INSERT INTO `sample_data` VALUES (14, NULL, '/file/sample_data/WCDMA_3.txt', 'FREQUENCY', 'WCDMA');
INSERT INTO `sample_data` VALUES (15, NULL, '/file/sample_data/WCDMA_4.txt', 'FREQUENCY', 'WCDMA');
INSERT INTO `sample_data` VALUES (16, NULL, '/file/sample_data/WCDMA_5.txt', 'FREQUENCY', 'WCDMA');
INSERT INTO `sample_data` VALUES (17, NULL, '/file/sample_data/WLAN_0.txt', 'FREQUENCY', 'WLAN');
INSERT INTO `sample_data` VALUES (18, NULL, '/file/sample_data/WLAN_1.txt', 'FREQUENCY', 'WLAN');
INSERT INTO `sample_data` VALUES (19, NULL, '/file/sample_data/WLAN_2.txt', 'FREQUENCY', 'WLAN');
INSERT INTO `sample_data` VALUES (20, NULL, '/file/sample_data/WLAN_3.txt', 'FREQUENCY', 'WLAN');
INSERT INTO `sample_data` VALUES (21, NULL, '/file/sample_data/WLAN_4.txt', 'FREQUENCY', 'WLAN');
INSERT INTO `sample_data` VALUES (22, NULL, '/file/sample_data/WLAN_5.txt', 'FREQUENCY', 'WLAN');
INSERT INTO `sample_data` VALUES (23, NULL, '/file/sample_data/WLAN_6.txt', 'FREQUENCY', 'WLAN');
INSERT INTO `sample_data` VALUES (24, NULL, '/file/sample_data/CDMA800_0.txt', 'FREQUENCY', 'CDMA800');
INSERT INTO `sample_data` VALUES (25, NULL, '/file/sample_data/CDMA800_1.txt', 'FREQUENCY', 'CDMA800');
INSERT INTO `sample_data` VALUES (26, NULL, '/file/sample_data/CDMA800_2.txt', 'FREQUENCY', 'CDMA800');
INSERT INTO `sample_data` VALUES (27, NULL, '/file/sample_data/CDMA800_3.txt', 'FREQUENCY', 'CDMA800');
INSERT INTO `sample_data` VALUES (28, NULL, '/file/sample_data/CDMA800_4.txt', 'FREQUENCY', 'CDMA800');
INSERT INTO `sample_data` VALUES (29, NULL, '/file/sample_data/CDMA800_5.txt', 'FREQUENCY', 'CDMA800');
INSERT INTO `sample_data` VALUES (30, NULL, '/file/sample_data/TD_SCDMA_0.txt', 'FREQUENCY', 'TD_SCDMA');
INSERT INTO `sample_data` VALUES (31, NULL, '/file/sample_data/TD_SCDMA_1.txt', 'FREQUENCY', 'TD_SCDMA');
INSERT INTO `sample_data` VALUES (32, NULL, '/file/sample_data/TD_SCDMA_2.txt', 'FREQUENCY', 'TD_SCDMA');
INSERT INTO `sample_data` VALUES (33, NULL, '/file/sample_data/FDD_LTE_0.txt', 'FREQUENCY', 'FDD-LTE');
INSERT INTO `sample_data` VALUES (34, NULL, '/file/sample_data/FDD_LTE_1.txt', 'FREQUENCY', 'FDD-LTE');
INSERT INTO `sample_data` VALUES (35, NULL, '/file/sample_data/FDD_LTE_2.txt', 'FREQUENCY', 'FDD-LTE');
INSERT INTO `sample_data` VALUES (36, NULL, '/file/sample_data/FDD_LTE_3.txt', 'FREQUENCY', 'FDD-LTE');
INSERT INTO `sample_data` VALUES (37, NULL, '/file/sample_data/GSM1800_0.txt', 'FREQUENCY', 'GSM1800');
INSERT INTO `sample_data` VALUES (38, NULL, '/file/sample_data/GSM1800_1.txt', 'FREQUENCY', 'GSM1800');
INSERT INTO `sample_data` VALUES (39, NULL, '/file/sample_data/GSM1800_2.txt', 'FREQUENCY', 'GSM1800');
INSERT INTO `sample_data` VALUES (40, NULL, '/file/sample_data/GSM1800_3.txt', 'FREQUENCY', 'GSM1800');
INSERT INTO `sample_data` VALUES (41, NULL, '/file/sample_data/GSM1800_4.txt', 'FREQUENCY', 'GSM1800');

-- ----------------------------
-- Table structure for steady_data
-- ----------------------------
DROP TABLE IF EXISTS `steady_data`;
CREATE TABLE `steady_data`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` bigint(20) NULL DEFAULT NULL,
  `data` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `report` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `item` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `place` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `remarks` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_data
-- ----------------------------
DROP TABLE IF EXISTS `sys_data`;
CREATE TABLE `sys_data`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `batch` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `create_time` bigint(20) NULL DEFAULT NULL,
  `data` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `envelope` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `exceed` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `frequencyl` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `frequencyr` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `item` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `layout` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `model` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `place` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `pol` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `report` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `spacecraft` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `stage` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `standard` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `state` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `test_obj` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for unit_data
-- ----------------------------
DROP TABLE IF EXISTS `unit_data`;
CREATE TABLE `unit_data`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `batch` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `create_time` bigint(20) NULL DEFAULT NULL,
  `data` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `envelope` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `equ_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `equ_number` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `exceed` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `frequencyl` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `frequencyr` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `item` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `layout` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `model` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `place` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `pol` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `report` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `spacecraft` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `stage` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `standard` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `state` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `subsys` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `test_obj` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for used_freq_point
-- ----------------------------
DROP TABLE IF EXISTS `used_freq_point`;
CREATE TABLE `used_freq_point`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `biz_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `create_time` bigint(20) NULL DEFAULT NULL,
  `freql` decimal(19, 2) NULL DEFAULT NULL,
  `freqr` decimal(19, 2) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 36 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of used_freq_point
-- ----------------------------
INSERT INTO `used_freq_point` VALUES (1, '调频广播', 1568877325376, 87.00, 108.00);
INSERT INTO `used_freq_point` VALUES (2, '农村无线接入', 1568877349372, 450.00, 470.00);
INSERT INTO `used_freq_point` VALUES (3, '数字电视、微波接力', 1568877370581, 470.00, 806.00);
INSERT INTO `used_freq_point` VALUES (4, 'CDMA800上行', 1568877384316, 825.00, 835.00);
INSERT INTO `used_freq_point` VALUES (5, 'CDMA800下行', 1568877395538, 870.00, 880.00);
INSERT INTO `used_freq_point` VALUES (6, 'EGSM900上行', 1568877409383, 885.00, 890.00);
INSERT INTO `used_freq_point` VALUES (7, 'GSM900上行', 1568877423596, 890.00, 909.00);
INSERT INTO `used_freq_point` VALUES (8, 'ISM频段', 1568877433657, 915.00, 917.00);
INSERT INTO `used_freq_point` VALUES (9, 'EGSM900下行', 1568877443121, 930.00, 935.00);
INSERT INTO `used_freq_point` VALUES (10, 'GSM900下行', 1568877453258, 935.00, 960.00);
INSERT INTO `used_freq_point` VALUES (11, '航空导航', 1568877465860, 960.00, 1215.00);
INSERT INTO `used_freq_point` VALUES (12, '科研、定位、导航', 1568877479916, 1215.00, 1260.00);
INSERT INTO `used_freq_point` VALUES (13, '空间科学、定位、导航', 1568877490707, 1260.00, 1300.00);
INSERT INTO `used_freq_point` VALUES (14, '航空导航、无线电定位', 1568877502994, 1300.00, 1350.00);
INSERT INTO `used_freq_point` VALUES (15, '点对点微波通信', 1568877515388, 1427.00, 1525.00);
INSERT INTO `used_freq_point` VALUES (16, '航空、卫星导航', 1568877527473, 1559.00, 1626.00);
INSERT INTO `used_freq_point` VALUES (17, '气象卫星通信', 1568877539490, 1660.00, 1710.00);
INSERT INTO `used_freq_point` VALUES (18, 'GSM1800上行', 1568877552071, 1710.00, 1745.00);
INSERT INTO `used_freq_point` VALUES (19, 'FDD-LTE上行', 1568877562605, 1755.00, 1780.00);
INSERT INTO `used_freq_point` VALUES (20, '民航', 1568877575313, 1785.00, 1805.00);
INSERT INTO `used_freq_point` VALUES (21, 'GSM1800下行', 1568877584976, 1805.00, 1840.00);
INSERT INTO `used_freq_point` VALUES (22, 'FDD-LTE下行', 1568877595323, 1850.00, 1875.00);
INSERT INTO `used_freq_point` VALUES (23, 'TD-SCDMA', 1568877611957, 1880.00, 1900.00);
INSERT INTO `used_freq_point` VALUES (24, 'CDMA2000上行', 1568877622831, 1920.00, 1935.00);
INSERT INTO `used_freq_point` VALUES (25, 'WCDMA上行', 1568877633187, 1940.00, 1955.00);
INSERT INTO `used_freq_point` VALUES (26, '卫星通信', 1568877642127, 1980.00, 2010.00);
INSERT INTO `used_freq_point` VALUES (27, 'TD-SCDMA', 1568877654047, 2010.00, 2025.00);
INSERT INTO `used_freq_point` VALUES (28, 'CDMA2000下行', 1568877669744, 2110.00, 2125.00);
INSERT INTO `used_freq_point` VALUES (29, 'WCDMA下行', 1568877680904, 2130.00, 2145.00);
INSERT INTO `used_freq_point` VALUES (30, 'TD-LTE', 1568877690457, 2300.00, 2390.00);
INSERT INTO `used_freq_point` VALUES (31, 'WLAN', 1568877705490, 2400.00, 2483.50);
INSERT INTO `used_freq_point` VALUES (33, '卫星广播', 1568877808255, 2500.00, 2535.00);
INSERT INTO `used_freq_point` VALUES (34, 'TD-LTE', 1568877817523, 2555.00, 2655.00);
INSERT INTO `used_freq_point` VALUES (35, '5Ghz无线电波', 1568877836930, 5725.00, 5850.00);

-- ----------------------------
-- Table structure for waterfall_data_pico
-- ----------------------------
DROP TABLE IF EXISTS `waterfall_data_pico`;
CREATE TABLE `waterfall_data_pico`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `data_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for waterfall_data_usrp1
-- ----------------------------
DROP TABLE IF EXISTS `waterfall_data_usrp1`;
CREATE TABLE `waterfall_data_usrp1`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `data_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 48 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for waterfall_data_usrp2
-- ----------------------------
DROP TABLE IF EXISTS `waterfall_data_usrp2`;
CREATE TABLE `waterfall_data_usrp2`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `data_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 49 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
