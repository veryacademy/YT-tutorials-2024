# SQL

### Return all constraints

```sql
SELECT 
    conname AS constraint_name,
    contype AS constraint_type,
    CASE WHEN contype = 'f' THEN pg_catalog.pg_get_constraintdef(c.oid, true)
         ELSE NULL END AS foreign_key_definition
FROM pg_catalog.pg_constraint c
JOIN pg_catalog.pg_class cls ON cls.oid = c.conrelid
JOIN pg_catalog.pg_namespace n ON n.oid = cls.relnamespace
WHERE n.nspname = 'public'  -- Replace with your schema if different
    AND cls.relname = 'inventory_category'
ORDER BY constraint_name;
```

### Query to View Specific Constraint Details

```sql
SELECT conname AS constraint_name, pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conname = 'inventory_seasonal_event_chk_empty_name';
```

### Query to View Specific Trigger Details

```sql
SELECT tgname AS trigger_name, pg_get_triggerdef(oid) AS trigger_definition
FROM pg_trigger
WHERE tgname = 'category_lowercase_name_trigger';
```

### Query to Check Indexes for a Table

```sql
SELECT
    indexname AS index_name,
    indexdef AS index_definition,
    tablename AS table_name
FROM pg_indexes
WHERE schemaname = 'public'  -- Replace with your schema name if different
    AND tablename = 'inventory_category';  -- Replace with your table name
```

### Identify columns that are defined as NOT NULL
```sql
SELECT 
    attname AS column_name,
    attnotnull AS not_null
FROM pg_catalog.pg_attribute
WHERE attrelid = 'public.inventory_category'::regclass  -- Replace with your schema.table
    AND attnum > 0
    AND attnotnull;
```

### View all table info
```sql
SELECT
    a.attname AS column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
    CASE WHEN a.attnotnull THEN 'NOT NULL' ELSE 'NULL' END AS nullability,
    CASE
        WHEN dc.contype = 'p' THEN 'PRIMARY KEY'
        WHEN dc.contype = 'f' THEN 'FOREIGN KEY'
        ELSE ''
    END AS constraint_type,
    dc.conname AS constraint_name,
    CASE WHEN dc.contype = 'f' THEN fkc.ref_table_name || '(' || fkc.ref_column_name || ')' ELSE '' END AS foreign_key_reference
FROM pg_catalog.pg_attribute a
JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN pg_catalog.pg_constraint dc ON dc.conrelid = c.oid AND a.attnum = ANY(dc.conkey)
LEFT JOIN (
    SELECT conrelid::regclass::text AS table_name,
           unnest(conkey) AS col_index,
           conname,
           pg_get_constraintdef(oid) AS condef,
           confrelid::regclass::text AS ref_table_name,
           unnest(confkey) AS ref_col_index,
           (SELECT attname FROM pg_attribute WHERE attrelid = confrelid AND attnum = ANY(confkey)) AS ref_column_name
    FROM pg_catalog.pg_constraint
) AS fkc ON fkc.table_name = c.relname::text AND fkc.col_index = a.attnum
WHERE n.nspname = 'public'  -- Replace with your schema name if different
    AND c.relname = 'inventory_tag'  -- Replace with your table name
    AND a.attnum > 0
GROUP BY a.attname, a.atttypid, a.atttypmod, a.attnotnull, dc.contype, dc.conname, fkc.ref_table_name, fkc.ref_column_name
ORDER BY column_name;  -- Changed to ORDER BY column_name to avoid using a.attnum directly
```