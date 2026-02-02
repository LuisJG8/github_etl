import duckdb 

duckdb.sql("SET display_max_rows=10000")

df = duckdb.read_parquet("../2026-02-02/github_data.parquet")

# duckdb.sql("DESCRIBE SELECT * FROM df").show()

# duckdb.sql("SELECT language, COUNT(language) AS c_p \
#             FROM df \
#             GROUP BY language \
#             ORDER BY c_p DESC").show()

duckdb.sql("DESCRIBE SELECT * FROM df").show()