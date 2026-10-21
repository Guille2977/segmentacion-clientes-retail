-- 01_limpieza.sql
-- Construye tablas filtradas a partir de transacciones_raw sin modificarla.

-- 1) Compras válidas de productos por clientes identificados
DROP TABLE IF EXISTS ventas_limpias;

CREATE TABLE ventas_limpias AS
SELECT DISTINCT                                   -- quita filas duplicadas exactas
    invoice,
    stock_code,
    description,
    quantity,
    invoice_date,
    price,
    customer_id,
    country,
    quantity * price AS total
FROM transacciones_raw
WHERE customer_id IS NOT NULL                     -- cliente identificado
  AND invoice NOT LIKE 'C%'                       -- no es cancelación
  AND quantity > 0
  AND price > 0
  AND UPPER(stock_code) NOT IN (                  -- códigos que no son productos
      'POST', 'DOT', 'M', 'D', 'S', 'C2', 'B', 'CRUK', 'PADS',
      'BANK CHARGES', 'ADJUST', 'ADJUST2', 'AMAZONFEE'
  )
  AND stock_code NOT LIKE 'gift%'                 -- vales de regalo
  AND stock_code NOT LIKE 'TEST%';                -- registros de prueba

-- 2) Devoluciones de productos por clientes identificados
DROP TABLE IF EXISTS devoluciones;

CREATE TABLE devoluciones AS
SELECT DISTINCT
    invoice,
    stock_code,
    description,
    quantity,
    invoice_date,
    price,
    customer_id,
    country,
    -quantity * price AS monto_devuelto           -- en positivo
FROM transacciones_raw
WHERE customer_id IS NOT NULL
  AND invoice LIKE 'C%'
  AND quantity < 0
  AND price > 0
  AND UPPER(stock_code) NOT IN (
      'POST', 'DOT', 'M', 'D', 'S', 'C2', 'B', 'CRUK', 'PADS',
      'BANK CHARGES', 'ADJUST', 'ADJUST2', 'AMAZONFEE'
  )
  AND stock_code NOT LIKE 'gift%'
  AND stock_code NOT LIKE 'TEST%';