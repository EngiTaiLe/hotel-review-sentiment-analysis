import mysql.connector
import traceback
import pandas as pd

class Connector:
    def __init__(self, host = None, port = None, database = None, username = None, password = None):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host = self.host,
                port = self.port,
                database = self.database,
                user = self.username,
                password = self.password
            )
            return self.conn

        except:
            self.conn = None
            traceback.print_exc()
        return

    def disConnect(self):
        if self.conn != None:
            self.conn.close()

    def queryData(self, sql, fetch=True):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)

            # Đảm bảo đã xử lý kết quả từ SELECT
            if fetch:
                # Kiểm tra xem câu lệnh có trả về dữ liệu không
                if cursor.with_rows:  # Kiểm tra xem có kết quả trả về không
                    results = cursor.fetchall()  # Đọc hết kết quả
                    df = pd.DataFrame(results)
                    if not df.empty:
                        df.columns = cursor.column_names
                    return df
                else:
                    # Nếu không có kết quả trả về, trả về DataFrame rỗng
                    return pd.DataFrame()

            else:
                # Nếu chỉ thực hiện lệnh INSERT/UPDATE, commit giao dịch
                self.conn.commit()
                return True

        except Exception as e:
            traceback.print_exc()
            return None

    # def queryData(self, sql, fetch=True):
    #     try:
    #         cursor = self.conn.cursor()
    #         cursor.execute(sql)
    #
    #         # Nếu fetch = True, thực hiện fetchall() nhưng chỉ khi có kết quả
    #         if fetch:
    #             results = cursor.fetchall()
    #             df = pd.DataFrame(results)
    #             if not df.empty:
    #                 df.columns = cursor.column_names
    #             return df
    #
    #         else:
    #             # Nếu chỉ thực hiện INSERT/UPDATE, commit giao dịch
    #             self.conn.commit()
    #             return True
    #
    #     except Exception as e:
    #         traceback.print_exc()
    #         return None

    # def queryData(self, sql, params=None, fetch=True):
    #     try:
    #         cursor = self.conn.cursor(dictionary=True)  # Trả kết quả dưới dạng dictionary
    #         if params:
    #             cursor.execute(sql, params)  # Sử dụng parameterized query
    #         else:
    #             cursor.execute(sql)
    #
    #         if fetch:
    #             df = pd.DataFrame(cursor.fetchall())
    #             if not df.empty:
    #                 df.columns = cursor.column_names
    #             return df
    #
    #         else:
    #             self.conn.commit()
    #             return True
    #
    #     except:
    #         traceback.print_exc()
    #         return None




