import cx_Oracle
import logging


class OracleWorker:
    def __init__(self, username, password, ip, port, sid):
        dsn = cx_Oracle.makedsn(ip, port, sid)
        self.db_conn = cx_Oracle.connect(username, password, dsn)
        self._cursor = self.db_conn.cursor()

    def __del__(self):
        self._cursor.close()
        self.db_conn.close()

    def get_cursor(self):
        return self._cursor

    def insert(self, table_name, *args, **kwargs):
        len_args = len(args)
        len_kwargs = len(kwargs)
        if len_args == 0 and len_kwargs == 0:
            logging.warning("No columns input!")
            return False

        if len_args > 0 and len_kwargs > 0:
            logging.warning("Usage: table emp (a, b, c)"
                            "OracleWriter.insert(emp, 1, 2, 3) or "
                            "OracleWriter.insert(emp, a, 1, b, 2, c, 3)")
            return False

        try:
            if len_args == 0:
                name_str = self.get_comma_str(kwargs.keys())
                var_str = self.get_comma_str(kwargs.keys(), ":")
                sql_str = "insert into %s(%s) values(%s)" % (table_name, name_str, var_str)
                self._cursor.execute(sql_str, kwargs)
            else:
                value_str = self.get_comma_str(args)
                sql_str = "insert into %s values(%s)" % (table_name, value_str)
                self._cursor.execute(sql_str)
        except cx_Oracle.DatabaseError as e:
            error = e.args[0]
            if hasattr(error, "code") and error.code == 1:
                # logging.info("Records already existed, do nothing.")
                # logging.info("  TABLE: %s" % table_name)
                # logging.info("  DATA: %s" % table_name)
                logging.debug(e)
                return False
        return True

    def commit(self):
        self.db_conn.commit()

    def rollback(self):
        self.db_conn.rollback()

    def select_max(self, table_name, column_name):
        sql_str = "select max(%s) from %s" % (column_name, table_name)
        self._cursor.execute(sql_str)
        return self._cursor.fetchone()

    def select_one(self, table_name, where_condition=None, columns="*"):
        self._select(columns, table_name, where_condition)
        return self._cursor.fetchone()

    def _select(self, columns, table_name, where_condition):
        if where_condition is None:
            sql_str = "select %s from %s" % (columns, table_name)
        else:
            sql_str = "select %s from %s where %s" % (columns, table_name, where_condition)
        self._cursor.execute(sql_str)

    def select_all(self, table_name, where_condition=None, columns="*"):
        self._select(columns, table_name, where_condition)
        return self._cursor.fetchall()

    def row_count(self):
        return self._cursor.rowcount

    def get_next_id(self, table_name):
        sql_str = "select " + table_name + "_SEQ.NEXTVAL from dual"
        self._cursor.execute(sql_str)
        nid = self._cursor.fetchone()
        return nid[0]

    def get_curr_id(self, table_name):
        sql_str = "select " + table_name + "_SEQ.CURRVAL from dual"
        self._cursor.execute(sql_str)
        cid = self._cursor.fetchone()
        return cid[0]

    @staticmethod
    def get_comma_str(seq, prefix=""):
        result_str = ""
        for value in seq:
            result_str += prefix + str(value) + ","
        result_str = result_str[:-1]
        return result_str

if __name__ == '__main__':
    __DB_USERNAME = "system"
    __DB_PASSWORD = "manager"
    __DB_IP = "localhost"
    __DB_PORT = "1521"
    __DB_SID = "ORCL"
    worker = OracleWorker(
        __DB_USERNAME,
        __DB_PASSWORD,
        __DB_IP,
        __DB_PORT,
        __DB_SID
    )
    self_id = worker.select_one(
        "COUNTRIES",
        where_condition="NAME = 英国",
        columns="ID"
    )


