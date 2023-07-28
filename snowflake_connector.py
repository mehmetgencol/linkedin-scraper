import snowflake.connector as connector
import snowflake.connector.pandas_tools as pandas_tools


class SnowflakeConnector:
    def __init__(self, user, password, account, db, schema, table, warehouse):
        self.table = table
        self.conn = connector.connect(
            user=user,
            password=password,
            account=account,
            ocsp_fail_open=False,
            database=db,
            schema=schema,
            warehouse=warehouse
        )

    def write_pandas(self, df):
        if self.conn:
            pandas_tools.write_pandas(self.conn, df, self.table, auto_create_table=True)
