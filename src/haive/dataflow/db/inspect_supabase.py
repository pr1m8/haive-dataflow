from haive.dataflow.db.db.supabase import (
    fetch_all_schemas_and_tables,
    fetch_foreign_key_relations,
    fetch_primary_keys,
    fetch_table_columns,
    get_supabase_client,
)


def main():
    client = get_supabase_client()

    for _row in fetch_all_schemas_and_tables(client):
        pass

    for _fk in fetch_foreign_key_relations(client):
        pass

    for _pk in fetch_primary_keys(client):
        pass

    for _col in fetch_table_columns(client):
        pass


if __name__ == "__main__":
    main()
