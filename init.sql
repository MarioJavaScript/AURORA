CREATE TABLE tipos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL UNIQUE
);
CREATE TABLE estados (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL UNIQUE
);
CREATE TABLE equipos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  clave VARCHAR(30) NOT NULL UNIQUE,
  tipo_id INT NOT NULL,
  marca VARCHAR(80) NOT NULL,
  modelo VARCHAR(100) NOT NULL,
  numero_serie VARCHAR(100) NOT NULL,
  estado_id INT NOT NULL,
  ubicacion VARCHAR(150) NOT NULL,
  cliente VARCHAR(150) NULL,
  fecha_alta DATE NOT NULL,
  notas TEXT NULL,
  FOREIGN KEY (tipo_id) REFERENCES tipos(id),
  FOREIGN KEY (estado_id) REFERENCES estados(id)
);
INSERT INTO tipos (nombre) VALUES
('Servidor'),('Firewall'),('Switch'),('Sensor de red'),('Laptop de analista'),('Monitor de SOC'),('UPS'),('Llave de seguridad');
INSERT INTO estados (nombre) VALUES
('Operativo'),('En monitoreo'),('En mantenimiento'),('En cuarentena'),('Fuera de servicio'),('Dado de baja');
INSERT INTO equipos (clave,tipo_id,marca,modelo,numero_serie,estado_id,ubicacion,cliente,fecha_alta,notas) VALUES
('SRV-01',1,'Dell','PowerEdge R650','FIC-SRV-0001',1,'Rack A oficina central',NULL,'2025-01-10','Servidor de laboratorio'),
('FW-02',2,'Fortinet','FortiGate 60F','FIC-FW-0002',3,'Rack A oficina central',NULL,'2025-01-12','Revisión programada'),
('SW-01',3,'Cisco','Catalyst 1000','FIC-SW-0001',1,'Rack B oficina central',NULL,'2025-01-15',NULL),
('SEN-03',4,'Raspberry Pi','5','FIC-SEN-0003',2,'Sucursal norte','Taquería La Ficticia','2025-02-01','Sensor de pruebas'),
('SEN-04',4,'Raspberry Pi','5','FIC-SEN-0004',5,'Almacén',NULL,'2025-02-02','Pendiente de diagnóstico'),
('LAP-07',5,'Lenovo','ThinkPad T14','FIC-LAP-0007',4,'Laboratorio de análisis',NULL,'2025-02-05','Aislamiento preventivo'),
('MON-02',6,'Samsung','32"','FIC-MON-0002',1,'Sala de monitoreo',NULL,'2025-02-06',NULL),
('UPS-01',7,'APC','Smart-UPS 1500','FIC-UPS-0001',1,'Rack A oficina central',NULL,'2025-02-07',NULL),
('SRV-02',1,'HPE','ProLiant DL380 Gen10','FIC-SRV-0002',1,'Rack B oficina central',NULL,'2025-02-09',NULL),
('FW-03',2,'Palo Alto Networks','PA-440','FIC-FW-0003',2,'Rack B oficina central','Consultoría Horizonte Ficticio','2025-02-10',NULL),
('LAP-08',5,'HP','EliteBook 840 G10','FIC-LAP-0008',1,'Sala de análisis',NULL,'2025-02-11',NULL),
('KEY-01',8,'Yubico','YubiKey 5 NFC','FIC-KEY-0001',6,'Archivo de activos',NULL,'2025-02-12','Baja simulada');
