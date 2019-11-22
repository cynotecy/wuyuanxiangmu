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
-- Records of emc_data
-- ----------------------------
INSERT INTO `emc_data` VALUES (19, '200.0', '94.5', 1568793693000, '/file/b43b249c-d9ea-11e9-a36a-a088699cd42e.dat', 'USRP', '测试1', 'FM:100.0%', '测试1', '教4', '', '', '/file/b4824c9e-d9ea-11e9-8e03-a088699cd42e.txt', NULL);
INSERT INTO `emc_data` VALUES (20, '200.0', '94.5', 1568794261000, '/file/eee85c02-d9eb-11e9-b649-a088699cd42e.dat', 'USRP', '测试2', 'FM', '测试2', '教四', '', '', '/file/eef09ae4-d9eb-11e9-b8d4-a088699cd42e.txt', NULL);
INSERT INTO `emc_data` VALUES (21, '200.0', '103.9', 1568794359000, '/file/345dbaa4-d9ec-11e9-9d61-a088699cd42e.dat', 'USRP', '测试3', 'FM', '测试3', '宿舍楼下', '', '', '/file/34602b86-d9ec-11e9-8a3d-a088699cd42e.txt', NULL);
INSERT INTO `emc_data` VALUES (22, '200.0', '104.0', 1568794474000, '/file/7d1c2894-d9ec-11e9-a12a-a088699cd42e.dat', 'USRP', '测试4', 'FM', '测试4', '宿舍楼下', '', '', '/file/7d204800-d9ec-11e9-bba5-a088699cd42e.txt', NULL);
INSERT INTO `emc_data` VALUES (23, '200.0', '940.6', 1568794474000, '/file/b09adf40-d9ec-11e9-a765-a088699cd42e.dat', 'USRP', '测试5', 'GMSK', '测试5', '食堂门口', '', '', '/file/b09c8d3e-d9ec-11e9-85e9-a088699cd42e.txt', NULL);
INSERT INTO `emc_data` VALUES (24, '200.0', '940.6', 1568794474000, '/file/d1c445a6-d9ec-11e9-822f-a088699cd42e.dat', 'USRP', '测试6', 'GMSK', '测试6', '食堂门口', '', '', '/file/d1c7a1a4-d9ec-11e9-9480-a088699cd42e.txt', NULL);
INSERT INTO `emc_data` VALUES (25, '200.0', '940.0', 1568795001000, '/file/a84e8de2-d9ed-11e9-b8b3-a088699cd42e.dat', 'USRP', '测试7', 'GMSK:81.25%,ASK:18.75%', '测试7', '教四楼下', '', '', '/file/a850d840-d9ed-11e9-89b5-a088699cd42e.txt', NULL);
INSERT INTO `emc_data` VALUES (26, '200.0', '1835.0', 1568795076000, '/file/d365d3ee-d9ed-11e9-bac7-a088699cd42e.dat', 'USRP', '测试8', 'GMSK:77.5%,FM:20.0%,BPSK:2.5%', '测试8', '教四楼下', '', '', '/file/d36b2c12-d9ed-11e9-863f-a088699cd42e.txt', NULL);
INSERT INTO `emc_data` VALUES (27, '200.0', '1835.0', 1568795076000, '/file/fa9eb2d8-d9ed-11e9-8ee6-a088699cd42e.dat', 'USRP', '测试9', 'GMSK:83.75%,OOK:7.5%,FM:6.25%', '测试9', '教一楼下', '', '', '/file/faa0fd2e-d9ed-11e9-903d-a088699cd42e.txt', NULL);
INSERT INTO `emc_data` VALUES (28, '200.0', '1807.0', 1568795472000, '/file/c50e6186-d9ee-11e9-b2e5-a088699cd42e.dat', 'USRP', '测试10', 'GMSK:97.5%,FM:2.5%', '测试10', '教一楼下', '', '', '/file/c514085e-d9ee-11e9-80df-a088699cd42e.txt', NULL);
INSERT INTO `emc_data` VALUES (29, '2000.0', '2347.0', 1568795595000, '/file/1718c02c-d9ef-11e9-94cc-a088699cd42e.dat', 'USRP', '测试11', 'OOK:51.249%,FM:32.5%,ASK:7.5%', '测试11', '科研楼', '', '', '/file/171b0a74-d9ef-11e9-b823-a088699cd42e.txt', NULL);
INSERT INTO `emc_data` VALUES (30, '1.0', '1.0', 1572074047000, '/file/4217c0d0-f7c0-11e9-9182-60f677a88dc3.dat', 'USRP', '', '1', '1', '', '', '', '/file/423b7a18-f7c0-11e9-b05d-60f677a88dc3.txt', NULL);
INSERT INTO `emc_data` VALUES (31, '3000.0', '1000.0', 1572851788000, '/file/236d4f52-fed3-11e9-924c-60f677a88dc3.dat', 'USRP', '', '2FSK:100.0%', 'test1', '', '', '', '/file/237149a6-fed3-11e9-9d23-60f677a88dc3.txt', NULL);

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
-- Records of freq_data
-- ----------------------------
INSERT INTO `freq_data` VALUES (6, 1568795751000, '/file/6cff9d48-d9ef-11e9-9afa-a088699cd42e.txt', '测试1', 'GSM1800', '测试1', '教四', '', 'USRP', 1805.00, 1840.00);
INSERT INTO `freq_data` VALUES (7, 1568795751000, '/file/952a01dc-d9ef-11e9-abcf-a088699cd42e.txt', '测试2', 'CDMA800', '测试2', '教四', '', 'USRP', 860.00, 880.00);
INSERT INTO `freq_data` VALUES (8, 1568795751000, '/file/a65c1422-d9ef-11e9-ab5a-a088699cd42e.txt', '测试3', 'WLAN', '测试3', '教四楼下', '', 'USRP', 2400.00, 2483.00);
INSERT INTO `freq_data` VALUES (9, 1568795751000, '/file/b9507358-d9ef-11e9-9ccd-a088699cd42e.txt', '测试4', 'WCDMA', '测试4', '教四楼下', '', 'USRP', 2130.00, 2145.00);
INSERT INTO `freq_data` VALUES (10, 1568795751000, '/file/d1635c52-d9ef-11e9-8ceb-a088699cd42e.txt', '测试5', 'GSM900', '测试5', '教一', '', 'USRP', 935.00, 960.00);
INSERT INTO `freq_data` VALUES (11, 1568795751000, '/file/21f623e2-d9f0-11e9-93b4-a088699cd42e.txt', '测试6', 'FDD_LTE', '测试6', '宿舍', '', 'USRP', 1850.00, 1875.00);
INSERT INTO `freq_data` VALUES (12, 1568795751000, '/file/44b18be4-d9f0-11e9-b841-a088699cd42e.txt', '测试7', 'TD_SCDMA', '测试7', '宿舍', '', 'USRP', 2010.00, 2025.00);
INSERT INTO `freq_data` VALUES (13, 1568795751000, '/file/792ad1f4-d9f0-11e9-9d81-a088699cd42e.txt', '测试8', 'WLAN', '测试8', '校门口', '', 'USRP', 2400.00, 2483.00);
INSERT INTO `freq_data` VALUES (14, 1568795751000, '/file/9b1a74d2-d9f0-11e9-9660-a088699cd42e.txt', '测试9', 'WCDMA', '测试9', '校门口', '', 'USRP', 2130.00, 2145.00);
INSERT INTO `freq_data` VALUES (15, 1568795751000, '/file/c6e05b76-d9f0-11e9-a608-a088699cd42e.txt', '测试10', 'GSM900', '测试10', '广场', '', 'USRP', 935.00, 960.00);
INSERT INTO `freq_data` VALUES (16, 1568795751000, '/file/ead7ec3e-d9f0-11e9-a6fc-a088699cd42e.txt', '测试11', 'GSM900', '测试11', '中心广场', '', 'USRP', 935.00, 960.00);
INSERT INTO `freq_data` VALUES (17, 1572074093000, '/file/550360fe-f7c0-11e9-b63b-60f677a88dc3.txt', '', '1', '1', '', '', 'USRP', 1.00, 1.00);

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
-- Records of label
-- ----------------------------
INSERT INTO `label` VALUES (1, '航天器2', '0', 'UNIT');

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
-- Records of operation
-- ----------------------------
INSERT INTO `operation` VALUES (1, '11', '现场干扰数据', '0:0:0:0:0:0:0:1', 1566990869104, '删除操作');
INSERT INTO `operation` VALUES (2, '12', '现场干扰数据', '0:0:0:0:0:0:0:1', 1566990871549, '删除操作');

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
-- Records of pulse_data
-- ----------------------------
INSERT INTO `pulse_data` VALUES (17, 1568959373000, '/file/663f142e-db6c-11e9-88b5-a088699cd42e.zip', '风扇', '测试1', '测试1', '教四', '');
INSERT INTO `pulse_data` VALUES (18, 1568959373000, '/file/7956bad8-db6c-11e9-8217-a088699cd42e.zip', '风扇', '测试2', '测试2', '教四', '');
INSERT INTO `pulse_data` VALUES (19, 1568959373000, '/file/86f1663e-db6c-11e9-896c-a088699cd42e.zip', '风扇', '测试3', '测试3', '教四', '');
INSERT INTO `pulse_data` VALUES (20, 1568959373000, '/file/93fae692-db6c-11e9-a1aa-a088699cd42e.zip', '电源', '测试4', '测试4', '教四', '');
INSERT INTO `pulse_data` VALUES (21, 1568959373000, '/file/a2b17392-db6c-11e9-83be-a088699cd42e.zip', '电源', '测试5', '测试5', '教四', '');
INSERT INTO `pulse_data` VALUES (22, 1568959373000, '/file/b5a753d8-db6c-11e9-9adf-a088699cd42e.zip', '电源', '测试6', '测试6', '教四', '');
INSERT INTO `pulse_data` VALUES (23, 1568959373000, '/file/c29c3c08-db6c-11e9-9c8b-a088699cd42e.zip', '适配器', '测试7', '测试7', '教四', '');
INSERT INTO `pulse_data` VALUES (24, 1568959373000, '/file/ce2816a2-db6c-11e9-8886-a088699cd42e.zip', '适配器', '测试8', '测试8', '教四', '');
INSERT INTO `pulse_data` VALUES (25, 1568959373000, '/file/dac24a10-db6c-11e9-aa3c-a088699cd42e.zip', '适配器', '测试9', '测试9', '教四', '');
INSERT INTO `pulse_data` VALUES (26, 1568959373000, '/file/eb0d0054-db6c-11e9-a561-a088699cd42e.zip', 'WD_200', '测试10', '测试10', '教四', '');
INSERT INTO `pulse_data` VALUES (27, 1568959373000, '/file/f92b5a52-db6c-11e9-bdd8-a088699cd42e.zip', 'WD_200', '测试11', '测试11', '教四', '');
INSERT INTO `pulse_data` VALUES (28, 1568959373000, '/file/0af5cb24-db6d-11e9-a872-a088699cd42e.zip', 'WD_200', '测试12', '测试12', '教四', '');
INSERT INTO `pulse_data` VALUES (29, 1572074156000, '/file/8226d24a-f7c0-11e9-9037-60f677a88dc3.rar', '1', '', '1', '', '');

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
-- Records of steady_data
-- ----------------------------
INSERT INTO `steady_data` VALUES (16, 1566458979000, '/file/b4fb8aa8-c4ae-11e9-9d92-f8a96341e539.txt', '/file/b4fcea82-c4ae-11e9-8552-f8a96341e539.txt', '项目名称', '信号名称', '', '备注');
INSERT INTO `steady_data` VALUES (17, 1572074221000, '/file/a76e3d6c-f7c0-11e9-a4ab-60f677a88dc3.txt', '/file/a7820e4a-f7c0-11e9-a009-60f677a88dc3.txt', '', '1', '', '');

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
-- Records of sys_data
-- ----------------------------
INSERT INTO `sys_data` VALUES (1, '1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

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
-- Records of unit_data
-- ----------------------------
INSERT INTO `unit_data` VALUES (1, '', 1561366039000, '/file/0348c527-555e-4d74-9d95-961cbcf73668.bat', NULL, '1', '', NULL, '', '', '1', NULL, '', '', '', NULL, '航天器2', '', '', '', '', '');

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
-- Records of waterfall_data_usrp1
-- ----------------------------
INSERT INTO `waterfall_data_usrp1` VALUES (1, '/file/waterfall/usrp1/4ed35300-ff8b-11e9-a098-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (2, '/file/waterfall/usrp1/4f75384f-ff8b-11e9-bc2e-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (3, '/file/waterfall/usrp1/5009b021-ff8b-11e9-8853-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (4, '/file/waterfall/usrp1/509e27f0-ff8b-11e9-a022-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (5, '/file/waterfall/usrp1/5137cfe1-ff8b-11e9-8835-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (6, '/file/waterfall/usrp1/51d59680-ff8b-11e9-9926-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (7, '/file/waterfall/usrp1/5268aec0-ff8b-11e9-88f8-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (8, '/file/waterfall/usrp1/52fcff80-ff8b-11e9-9a05-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (9, '/file/waterfall/usrp1/539bd78f-ff8b-11e9-a952-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (10, '/file/waterfall/usrp1/5432994f-ff8b-11e9-b442-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (11, '/file/waterfall/usrp1/54c7fb80-ff8b-11e9-8fb7-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (12, '/file/waterfall/usrp1/5561ca80-ff8b-11e9-a9b1-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (13, '/file/waterfall/usrp1/55f90170-ff8b-11e9-8807-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (14, '/file/waterfall/usrp1/56903861-ff8b-11e9-9ef0-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (15, '/file/waterfall/usrp1/572cc680-ff8b-11e9-ab27-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (16, '/file/waterfall/usrp1/57c90680-ff8b-11e9-9421-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (17, '/file/waterfall/usrp1/586175f0-ff8b-11e9-982a-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (18, '/file/waterfall/usrp1/58fcf2a1-ff8b-11e9-a17a-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (19, '/file/waterfall/usrp1/5990a721-ff8b-11e9-b52d-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (20, '/file/waterfall/usrp1/5a26cc9e-ff8b-11e9-81e0-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (21, '/file/waterfall/usrp1/5ac35ac0-ff8b-11e9-8478-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (22, '/file/waterfall/usrp1/5b578470-ff8b-11e9-9132-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (23, '/file/waterfall/usrp1/5bee944f-ff8b-11e9-aa99-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (24, '/file/waterfall/usrp1/5c88634f-ff8b-11e9-9ea8-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (25, '/file/waterfall/usrp1/5d21bd1e-ff8b-11e9-a165-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (26, '/file/waterfall/usrp1/5dbc4f70-ff8b-11e9-85b1-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (27, '/file/waterfall/usrp1/5e5c38f0-ff8b-11e9-bbf7-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (28, '/file/waterfall/usrp1/5ef65611-ff8b-11e9-98fc-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (29, '/file/waterfall/usrp1/5f859dc0-ff8b-11e9-9765-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (30, '/file/waterfall/usrp1/6021688f-ff8b-11e9-89b7-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (31, '/file/waterfall/usrp1/60b59240-ff8b-11e9-a48d-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (32, '/file/waterfall/usrp1/614cf040-ff8b-11e9-9cd5-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (33, '/file/waterfall/usrp1/61f209de-ff8b-11e9-b887-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (34, '/file/waterfall/usrp1/6282b11e-ff8b-11e9-9f80-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (35, '/file/waterfall/usrp1/631ad26e-ff8b-11e9-becd-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (36, '/file/waterfall/usrp1/63b40530-ff8b-11e9-8c20-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (37, '/file/waterfall/usrp1/644f5acf-ff8b-11e9-8c8e-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (38, '/file/waterfall/usrp1/64e55940-ff8b-11e9-8c61-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (39, '/file/waterfall/usrp1/657feb8f-ff8b-11e9-9505-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (40, '/file/waterfall/usrp1/66137900-ff8b-11e9-8cb9-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (41, '/file/waterfall/usrp1/66ab251e-ff8b-11e9-95f4-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (42, '/file/waterfall/usrp1/67478c30-ff8b-11e9-923a-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (43, '/file/waterfall/usrp1/67e72791-ff8b-11e9-92ab-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (44, '/file/waterfall/usrp1/687bc670-ff8b-11e9-97a4-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (45, '/file/waterfall/usrp1/690e6980-ff8b-11e9-bca5-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (46, '/file/waterfall/usrp1/69a886a1-ff8b-11e9-a2f9-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp1` VALUES (47, '/file/waterfall/usrp1/6a434000-ff8b-11e9-b2df-60f677a88dc3.dat');

-- ----------------------------
-- Table structure for waterfall_data_usrp2
-- ----------------------------
DROP TABLE IF EXISTS `waterfall_data_usrp2`;
CREATE TABLE `waterfall_data_usrp2`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `data_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 49 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of waterfall_data_usrp2
-- ----------------------------
INSERT INTO `waterfall_data_usrp2` VALUES (1, '/file/waterfall/usrp2/4e7a0f70-ff8b-11e9-8eee-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (2, '/file/waterfall/usrp2/4f0f4a8f-ff8b-11e9-a467-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (3, '/file/waterfall/usrp2/4fb4160f-ff8b-11e9-ac21-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (4, '/file/waterfall/usrp2/50430f9e-ff8b-11e9-8696-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (5, '/file/waterfall/usrp2/50d64eee-ff8b-11e9-b7f8-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (6, '/file/waterfall/usrp2/5175ea4f-ff8b-11e9-af8f-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (7, '/file/waterfall/usrp2/520d6f5e-ff8b-11e9-9021-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (8, '/file/waterfall/usrp2/52a0879e-ff8b-11e9-9766-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (9, '/file/waterfall/usrp2/53468b9e-ff8b-11e9-a9d1-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (10, '/file/waterfall/usrp2/53d8e091-ff8b-11e9-8a61-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (11, '/file/waterfall/usrp2/546dcd8f-ff8b-11e9-a287-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (12, '/file/waterfall/usrp2/5502ba8f-ff8b-11e9-9613-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (13, '/file/waterfall/usrp2/55a38e6e-ff8b-11e9-aabb-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (14, '/file/waterfall/usrp2/563ac561-ff8b-11e9-b4d3-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (15, '/file/waterfall/usrp2/56d5309e-ff8b-11e9-98b7-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (16, '/file/waterfall/usrp2/5769cf80-ff8b-11e9-8e3f-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (17, '/file/waterfall/usrp2/5804d700-ff8b-11e9-9dd1-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (18, '/file/waterfall/usrp2/589b71ae-ff8b-11e9-bb26-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (19, '/file/waterfall/usrp2/592f4d40-ff8b-11e9-9afc-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (20, '/file/waterfall/usrp2/59cb8d40-ff8b-11e9-b0f8-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (21, '/file/waterfall/usrp2/5a63ae8f-ff8b-11e9-9f61-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (22, '/file/waterfall/usrp2/5afb81c0-ff8b-11e9-a9b3-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (23, '/file/waterfall/usrp2/5b9550c0-ff8b-11e9-a2ec-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (24, '/file/waterfall/usrp2/5c2f46cf-ff8b-11e9-8075-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (25, '/file/waterfall/usrp2/5ccaea8f-ff8b-11e9-9d6b-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (26, '/file/waterfall/usrp2/5d5c7c30-ff8b-11e9-a9fa-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (27, '/file/waterfall/usrp2/5dfdec51-ff8b-11e9-9096-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (28, '/file/waterfall/usrp2/5e94d51e-ff8b-11e9-b63f-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (29, '/file/waterfall/usrp2/5f2c8140-ff8b-11e9-8be2-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (30, '/file/waterfall/usrp2/5fc565de-ff8b-11e9-9533-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (31, '/file/waterfall/usrp2/60576cb0-ff8b-11e9-b6fd-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (32, '/file/waterfall/usrp2/60efdc21-ff8b-11e9-923e-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (33, '/file/waterfall/usrp2/618f024f-ff8b-11e9-96be-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (34, '/file/waterfall/usrp2/6228aa40-ff8b-11e9-be32-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (35, '/file/waterfall/usrp2/62c2a051-ff8b-11e9-8ed4-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (36, '/file/waterfall/usrp2/63578d4f-ff8b-11e9-9969-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (37, '/file/waterfall/usrp2/63f3310f-ff8b-11e9-b9a2-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (38, '/file/waterfall/usrp2/648c15b0-ff8b-11e9-9da6-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (39, '/file/waterfall/usrp2/6523e8e1-ff8b-11e9-a9aa-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (40, '/file/waterfall/usrp2/65b77651-ff8b-11e9-b5ae-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (41, '/file/waterfall/usrp2/66505af0-ff8b-11e9-aebc-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (42, '/file/waterfall/usrp2/66e9dbcf-ff8b-11e9-9974-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (43, '/file/waterfall/usrp2/6781d60f-ff8b-11e9-b380-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (44, '/file/waterfall/usrp2/681f2780-ff8b-11e9-adf7-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (45, '/file/waterfall/usrp2/68b748cf-ff8b-11e9-90fb-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (46, '/file/waterfall/usrp2/6952ec8f-ff8b-11e9-8565-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (47, '/file/waterfall/usrp2/69e5b6b0-ff8b-11e9-92e0-60f677a88dc3.dat');
INSERT INTO `waterfall_data_usrp2` VALUES (48, '/file/waterfall/usrp2/6a7c5161-ff8b-11e9-bc58-60f677a88dc3.dat');

SET FOREIGN_KEY_CHECKS = 1;
