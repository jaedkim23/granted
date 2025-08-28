import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import datetime as datetime
from CAS_func_July2025 import *

load_dotenv()  # Loads variables from .env into environment

db_host = os.getenv('HOST')
db_name = os.getenv('DATABASE')
db_user = os.getenv('USERNAME')
db_password = os.getenv('PASSWORD')
db_port = os.getenv('PORT', 3306)  # Default to 3306 if not set
db_user = 'admin'
engine_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(engine_url, echo=False)
con = engine.connect()

check_duplicate_qry =  """
                        SELECT res_id, wos_id, alex_id, COUNT(*)
                        FROM id_lookup
                        GROUP BY res_id, wos_id, alex_id
                        HAVING COUNT(*) > 1
                        """

lookup_id = pd.read_sql(check_duplicate_qry, con)
# lookup_id.shape
delete_duplicate_qry = """
                        WITH ranked AS (
                        SELECT *,
                                ROW_NUMBER() OVER (
                                PARTITION BY res_id, wos_id, alex_id
                                ORDER BY res_id
                                ) AS rn
                            FROM id_lookup
                        )
                        DELETE FROM id_lookup
                        WHERE res_id IN (
                            SELECT res_id FROM ranked WHERE rn > 1)
                        """

con.execute(text(delete_duplicate_qry))
con.commit()

get_qry = "SELECT * FROM id_lookup"
lookup_id = pd.read_sql(get_qry, con)
duplicates = lookup_id[lookup_id.duplicated(subset=['res_id', 'wos_id', 'alex_id'], keep=False)]
# duplicates.shape