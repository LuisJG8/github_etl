import polars as pl
# from worker import get_github_data
import json

# result = get_github_data.delay()
# repo = result.get(timeout=60)
# print(repo)

df_json = pl.read_json("./data/github_repos.json")
print(df_json)

result = df_json.select(
    pl.col("language")
)

print(result)

df_json.write_parquet("myoutput.parquet")