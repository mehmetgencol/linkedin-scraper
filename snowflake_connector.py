import datetime

import snowflake.connector as connector
import snowflake.connector.pandas_tools as pandas_tools

from globals import DATE_FORMAT, POSTED_AT


class SnowflakeConnector:
    def __init__(self, user, password, account, db, schema, table, warehouse):
        self.user = user
        self.password = password
        self.account = account
        self.db = db
        self.schema = schema
        self.table = table
        self.warehouse = warehouse
        self._conn = None

    def get_conn(self):
        if not self._conn or self._conn.is_closed():
            self._conn = connector.connect(
                user=self.user,
                password=self.password,
                account=self.account,
                ocsp_fail_open=False,
                database=self.db,
                schema=self.schema,
                warehouse=self.warehouse
            )
        return self._conn

    def write_pandas(self, df):
        pandas_tools.write_pandas(self.get_conn(), df, self.table, auto_create_table=True)

    def clear_depends_on(self, older_than=30):
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=older_than)
        date_parsed = earliest_date.strftime(DATE_FORMAT)
        query = f'''DELETE FROM {self.table} WHERE "{POSTED_AT}" < '{date_parsed}' '''
        self.get_conn().cursor().execute(query)
        self.get_conn().commit()
