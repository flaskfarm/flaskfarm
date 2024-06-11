import traceback
from datetime import datetime, timedelta

from framework import F
from sqlalchemy import desc, or_


class ModelBase(F.db.Model):
    __abstract__ = True
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    P = None

    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        return {x.name: getattr(self, x.name).strftime('%m-%d %H:%M:%S') if isinstance(getattr(self, x.name), datetime) else getattr(self, x.name) for x in self.__table__.columns}
    

    def save(self):
        try:
            with F.app.app_context():
                F.db.session.add(self)
                F.db.session.commit()
                return self
        except Exception as e:
            self.P.logger.error(f'Exception:{str(e)}')
            self.P.logger.error(traceback.format_exc())

    @classmethod
    def get_paging_info(cls, count, current_page, page_size):
        try:
            paging = {}
            paging['prev_page'] = True
            paging['next_page'] = True
            if current_page <= 10:
                paging['prev_page'] = False
            
            paging['total_page'] = int(count / page_size) + 1
            if count % page_size == 0:
                paging['total_page'] -= 1
            paging['start_page'] = int((current_page-1)/10) * 10 + 1
            paging['last_page'] = paging['total_page'] if paging['start_page'] + 9 > paging['total_page'] else paging['start_page'] + 9
            if paging['last_page'] == paging['total_page']:
                paging['next_page'] = False
            paging['current_page'] = current_page
            paging['count'] = count
            #F.logger.debug('paging : c:%s %s %s %s %s %s', count, paging['total_page'], paging['prev_page'], paging['next_page'] , paging['start_page'], paging['last_page'])
            return paging
        except Exception as e:
            cls.P.logger.error(f'Exception:{str(e)}')
            cls.P.logger.error(traceback.format_exc())

    
    @classmethod
    def get_by_id(cls, id):
        try:
            with F.app.app_context():
                return F.db.session.query(cls).filter_by(id=int(id)).first()
        except Exception as e:
            cls.P.logger.error(f'Exception:{str(e)}')
            cls.P.logger.error(traceback.format_exc())


    @classmethod
    def get_list(cls, by_dict=False):
        try:
            with F.app.app_context():
                tmp = F.db.session.query(cls).all()
                if by_dict:
                    tmp = [x.as_dict() for x in tmp]
                return tmp
        except Exception as e:
            cls.P.logger.error(f'Exception:{str(e)}')
            cls.P.logger.error(traceback.format_exc())



    @classmethod
    def delete_by_id(cls, id):
        try:
            with F.app.app_context():
                F.db.session.query(cls).filter_by(id=int(id)).delete()
                F.db.session.commit()
                return True
        except Exception as e:
            cls.P.logger.error(f'Exception:{str(e)}')
            cls.P.logger.error(traceback.format_exc())
        return False

    @classmethod
    def delete_all(cls, day=None):
        count = -1
        try:
            with F.app.app_context():
                if day == None or day in [0, '0']:
                    count = F.db.session.query(cls).delete()
                else:
                    now = datetime.now()
                    ago = now - timedelta(days=int(day))
                    #ago.hour = 0
                    #ago.minute = 0
                    count = F.db.session.query(cls).filter(cls.created_time < ago).delete()
                    cls.P.logger.info(f"delete_all {day=} {count=}")
                F.db.session.commit()
            
            with F.app.app_context():
                F.db.session.execute('VACCUM;')
        except Exception as e:
            cls.P.logger.error(f'Exception:{str(e)}')
            cls.P.logger.error(traceback.format_exc())
        return count
    

    @classmethod
    def web_list(cls, req):
        try:
            ret = {}
            page = 1
            page_size = 30
            search = ''
            if 'page' in req.form:
                page = int(req.form['page'])
            if 'keyword' in req.form:
                search = req.form['keyword'].strip()
            option1 = req.form.get('option1', 'all')
            option2 = req.form.get('option2', 'all')
            order = req.form['order'] if 'order' in req.form else 'desc'

            query = cls.make_query(req, order=order, search=search, option1=option1, option2=option2)
            count = query.count()
            query = query.limit(page_size).offset((page-1)*page_size)
            #F.logger.debug('cls count:%s', count)
            lists = query.all()
            ret['list'] = [item.as_dict() for item in lists]
            ret['paging'] = cls.get_paging_info(count, page, page_size)
            try:
                if cls.P.ModelSetting is not None and cls.__tablename__ is not None:
                    cls.P.ModelSetting.set(f'{cls.__tablename__}_last_list_option', f'{order}|{page}|{search}|{option1}|{option2}')
            except Exception as e:
                F.logger.error(f"Exception:{str(e)}")
                F.logger.error(traceback.format_exc())
                F.logger.error(f'{cls.__tablename__}_last_list_option ERROR!' )
            return ret
        except Exception as e:
            cls.P.logger.error(f"Exception:{str(e)}")
            cls.P.logger.error(traceback.format_exc())


    # 오버라이딩
    @classmethod
    def make_query(cls, req, order='desc', search='', option1='all', option2='all'):
        with F.app.app_context():
            query = F.db.session.query(cls)
            if order == 'desc':
                query = query.order_by(desc(cls.id))
            else:
                query = query.order_by(cls.id)
            return query 
        
    
    @classmethod
    def make_query_search(cls, query, search, field):
        if search is not None and search != '':
            if search.find('|') != -1:
                tmp = search.split('|')
                conditions = []
                for tt in tmp:
                    if tt != '':
                        conditions.append(field.like('%'+tt.strip()+'%') )
                query = query.filter(or_(*conditions))
            elif search.find(',') != -1:
                tmp = search.split(',')
                for tt in tmp:
                    if tt != '':
                        query = query.filter(field.like('%'+tt.strip()+'%'))
            else:
                query = query.filter(field.like('%'+search+'%'))
            #query = query1.union(query2)
        return query
