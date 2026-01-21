from datetime import datetime, timezone



iso_value   = "2026-01-20T23:59:59.999999+00:00"
# parse ISO
dt = datetime.fromisoformat(iso_value)

# normalize to UTC and drop tzinfo for SQL
dt_sql = dt.astimezone(timezone.utc).replace(tzinfo=None)

print("Original ISO:", iso_value)
print("Parsed datetime:", dt)   
print("Datetime for SQL (UTC):", dt_sql)


# sql_value   = "2026-01-20 23:59:59.99999"

# dt = datetime.fromisoformat(sql_value)
# # dt = datetime.strptime(sql_value, "%Y-%m-%d %H:%M:%S.%f")

# def sql_datetime2_to_iso(dt_sql: datetime) -> str:
#     if dt_sql.tzinfo is not None:
#         raise ValueError("Expected naive datetime from datetime2")
#     return dt_sql.replace(tzinfo=timezone.utc).isoformat()

# iso_date=sql_datetime2_to_iso(dt)


# print("ISO date:", iso_date)