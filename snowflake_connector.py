import snowflake.connector as connector
import snowflake.connector.pandas_tools as pandas_tools


class SnowflakeConnector:
    def __init__(self, user, password, account, tag):
        self.con = connector.connect(
            user=user,
            password=password,
            account=account,
            session_parameters={
                'QUERY_TAG': tag,
            }
        )
        self.con.connect()
        self.table_name = "JobOpenings"

    def write_pandas(self, df):
        if self.con:
            pandas_tools.write_pandas(self.con, df, self.table_name)
