import sqlmodel

import services.database


def truncate(db: sqlmodel.Session):
    table_names = ["variants", "products", "vendors", "vendor_stock_locations", "variant_prules"]

    for table_name in table_names:
        services.database.truncate_table(db=db, table_name=table_name)
