# idacg

## build

```sh
uv run --group build python script/gen.py
```

## Reference

### DuckDB

read & write jsonl

```sql
COPY (
    SELECT *
    FROM read_ndjson_auto('functions.jsonl')
    WHERE export = true
)
TO 'exports.jsonl'
(FORMAT JSON, ARRAY false);
```
