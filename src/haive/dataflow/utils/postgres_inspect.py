import psycopg2
from rich.tree import Tree


def inspect_postgres(
    host: str = "localhost",
    dbname: str = "postgres",
    user: str = "postgres",
    password: str = "",
    port: int = 5432,
) -> Tree:
    """Inspect PostgreSQL schemas, tables, columns, and foreign keys.

    Returns:
        A rich.tree.Tree object representing the database structure.
    """
    conn = psycopg2.connect(
        host=host,
        dbname=dbname,
        user=user,
        password=password,
        port=port,
    )
    cursor = conn.cursor()

    # Get all user-defined tables
    cursor.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name;
    """)
    tables = cursor.fetchall()

    # Get columns
    cursor.execute("""
        SELECT table_schema, table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name, ordinal_position;
    """)
    columns = cursor.fetchall()

    # Get foreign keys
    cursor.execute("""
        SELECT
            tc.table_schema AS source_schema,
            tc.table_name AS source_table,
            kcu.column_name AS source_column,
            ccu.table_schema AS target_schema,
            ccu.table_name AS target_table,
            ccu.column_name AS target_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
           AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
           AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY';
    """)
    foreign_keys = cursor.fetchall()

    # Index data
    column_map = {}
    for schema, table, col, dtype in columns:
        column_map.setdefault((schema, table), []).append((col, dtype))

    fk_map = {}
    for src_schema, src_table, src_col, tgt_schema, tgt_table, tgt_col in foreign_keys:
        fk_map.setdefault((src_schema, src_table), []).append(
            f"{src_col} ➜ {tgt_schema}.{tgt_table}({tgt_col})"
        )

    # Build tree
    tree = Tree("📦 [bold green]PostgreSQL Schemas and Tables")
    for schema, table in tables:
        table_node = tree.add(f"🗂️ [cyan]{schema}[/].[bold]{table}[/]")
        for col, dtype in column_map.get((schema, table), []):
            table_node.add(f"🔹 [yellow]{col}[/] : [magenta]{dtype}[/]")
        if (schema, table) in fk_map:
            fk_node = table_node.add("🔗 [red]Foreign Keys[/]")
            for fk in fk_map[(schema, table)]:
                fk_node.add(fk)

    cursor.close()
    conn.close()
    return tree
