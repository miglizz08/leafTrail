CREATE DATABASE IF NOT EXISTS leaftrail
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE leaftrail;

CREATE TABLE IF NOT EXISTS gastos (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  data DATE NOT NULL,
  valor DECIMAL(10, 2) NOT NULL,
  categoria ENUM(
    'alimentacao',
    'transporte',
    'lazer',
    'contas_assinaturas',
    'outros'
  ) NOT NULL,
  descricao VARCHAR(255) NULL,
  CONSTRAINT chk_gastos_valor_positivo CHECK (valor > 0)
) ENGINE=InnoDB;
