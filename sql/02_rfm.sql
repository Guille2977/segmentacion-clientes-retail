-- 02_rfm.sql
-- Calcula Recency, Frequency y Monetary por cliente, más su tasa de devolución.

DROP TABLE IF EXISTS rfm;

CREATE TABLE rfm AS
WITH fecha_ref AS (                                  -- "hoy" = día siguiente a la última venta
    SELECT DATE(MAX(invoice_date), '+1 day') AS fecha
    FROM ventas_limpias
),
compras AS (                                         -- métricas de compra por cliente
    SELECT
        customer_id,
        MAX(country)            AS country,
        MIN(invoice_date)       AS primera_compra,
        MAX(invoice_date)       AS ultima_compra,
        COUNT(DISTINCT invoice) AS frequency,
        SUM(total)              AS monetary
    FROM ventas_limpias
    GROUP BY customer_id
),
devs AS (                                            -- monto devuelto por cliente
    SELECT customer_id, SUM(monto_devuelto) AS monto_devuelto
    FROM devoluciones
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    c.country,
    CAST(julianday(f.fecha) - julianday(c.ultima_compra) AS INTEGER) AS recency,
    c.frequency,
    ROUND(c.monetary, 2)                                AS monetary,
    ROUND(COALESCE(d.monto_devuelto, 0), 2)             AS monto_devuelto,
    ROUND(COALESCE(d.monto_devuelto, 0) / c.monetary, 4) AS tasa_devolucion,
    c.primera_compra,
    c.ultima_compra
FROM compras c
CROSS JOIN fecha_ref f
LEFT JOIN devs d ON d.customer_id = c.customer_id;