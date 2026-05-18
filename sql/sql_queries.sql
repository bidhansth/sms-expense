-- Monthly spend trend
SELECT
    DATE_TRUNC('month', txn_date)::date AS month,
    SUM(amount) AS total_amount
FROM transactions
WHERE txn_date BETWEEN :start_date AND :end_date
GROUP BY 1
ORDER BY 1;

-- Category breakdown
SELECT
    category,
    SUM(amount) AS total_amount
FROM transactions
WHERE txn_date BETWEEN :start_date AND :end_date
GROUP BY 1
ORDER BY total_amount DESC;
