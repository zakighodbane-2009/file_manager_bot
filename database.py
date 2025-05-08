import sqlite3
import datetime
class Data:
    def __init__(self,db_name='data.db'):
        self.db_name = db_name
        self._db_setup()
    def _connect(self):
        return sqlite3.connect(self.db_name)
    def _db_setup(self):
        with self._connect() as conn:
            cr = conn.cursor()
            cr.execute('create table if not exists data (' \
            'id integer primary key,' \
            'user_id integer,' \
            'file_id text,' \
            'time_update text,' \
            'file_size integer,' \
            'file_name text,' \
            'file_type text)')
            conn.commit()
    def save_data(self,user_id,file_or_phto_id,file_size,file_name,file_type):   
        time_update =  datetime.datetime.now().time().strftime('%H:%M:%S')
        with self._connect() as conn:
            cr = conn.cursor()
            cr.execute('insert into data (user_id,file_id,time_update,file_size,file_name,file_type) values(?,?,?,?,?,?)',(user_id,file_or_phto_id,time_update,file_size,file_name,file_type))
            conn.commit()
    def delete_file_by_id(self,id):
        with self._connect() as conn:
            cr = conn.cursor()
            cr.execute('delete from data where id=? ',(id,))
            conn.commit()
    def get_user_files(self,user_id):
        with self._connect() as conn:
            cr = conn.cursor()
            cr.execute('SELECT id, file_name, file_id FROM data WHERE user_id=?', (user_id,))
            list_file_downlad = cr.fetchall()
        return list_file_downlad