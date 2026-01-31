import duckdb 

df = duckdb.read_parquet("../2026-01-14/hey.parquet")

duckdb.sql("DESCRIBE SELECT * FROM df").show()

duckdb.sql("SELECT language, COUNT(language) AS c_p \
            FROM df \
            GROUP BY language \
            ORDER BY c_p DESC").show()