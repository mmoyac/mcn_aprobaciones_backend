-- Estructura real (sin datos) tomada con SHOW CREATE TABLE el 2026-09-30.
-- origen: lexascl_reppdf
CREATE DATABASE IF NOT EXISTS t_reppdf;
USE t_reppdf;

CREATE TABLE `pdf001` (
  `PdfEmpId` mediumint(9) NOT NULL AUTO_INCREMENT,
  `PdfEmpCd` smallint(6) NOT NULL,
  `PdfLocCod` smallint(6) NOT NULL,
  `PdfTipo` smallint(6) NOT NULL,
  `PdfNumero` bigint(20) NOT NULL,
  `PdfBlob` longblob NOT NULL,
  PRIMARY KEY (`PdfEmpId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
