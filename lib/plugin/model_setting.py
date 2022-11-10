import traceback
from datetime import datetime

from framework import F


def get_model_setting(package_name, logger, table_name=None):

    class ModelSetting(F.db.Model):
        __tablename__ = '%s_setting' % package_name if table_name is None else table_name
        __table_args__ = {'mysql_collate': 'utf8_general_ci'}
        __bind_key__ = package_name

        id = F.db.Column(F.db.Integer, primary_key=True)
        key = F.db.Column(F.db.String, unique=True, nullable=False)
        value = F.db.Column(F.db.String, nullable=False)
    
        def __init__(self, key, value):
            self.key = key
            self.value = value

        def __repr__(self):
            return repr(self.as_dict())

        def as_dict(self):
            return {x.name: getattr(self, x.name) for x in self.__table__.columns}

        @staticmethod
        def get(key):
            try:
                with F.app.app_context():
                    ret = F.db.session.query(ModelSetting).filter_by(key=key).first()
                    if ret is not None:
                        return ret.value.strip()
                    return None
            except Exception as e:
                logger.error(f"Exception:{str(e)} [{key}]")
                logger.error(traceback.format_exc())

        @staticmethod
        def has_key(key):
            with F.app.app_context():
                return (F.db.session.query(ModelSetting).filter_by(key=key).first() is not None)
        
        @staticmethod
        def get_int(key):
            try:
                return int(ModelSetting.get(key))
            except Exception as e:
                logger.error(f"Exception:{str(e)} [{key}]")
                logger.error(traceback.format_exc())
        
        @staticmethod
        def get_bool(key):
            try:
                return (ModelSetting.get(key) == 'True')
            except Exception as e:
                logger.error(f"Exception:{str(e)} [{key}]")
                logger.error(traceback.format_exc())
        
        @staticmethod
        def get_datetime(key):
            try:
                tmp = ModelSetting.get(key)
                if tmp != None and tmp != '':
                    return datetime.strptime(tmp, '%Y-%m-%d %H:%M:%S.%f')
            except Exception as e:
                logger.error(f"Exception:{str(e)} [{key}]")
                logger.error(traceback.format_exc())

        @staticmethod
        def set(key, value):
            try:
                with F.app.app_context():
                    item = F.db.session.query(ModelSetting).filter_by(key=key).with_for_update().first()
                    if item is not None:
                        item.value = value.strip() if value is not None else value
                        F.db.session.commit()
                    else:
                        F.db.session.add(ModelSetting(key, value.strip()))
                        F.db.session.commit()
            except Exception as e:
                logger.error(f"Exception:{str(e)} [{key}]")
                logger.error(traceback.format_exc())

        @staticmethod
        def to_dict():
            try:
                ret = ModelSetting.db_list_to_dict(F.db.session.query(ModelSetting).all())
                ret['package_name'] = package_name
                return ret 
            except Exception as e:
                logger.error(f"Exception:{str(e)}")
                logger.error(traceback.format_exc())


        @staticmethod
        def setting_save(req):
            try:
                change_list = []
                for key, value in req.form.items():
                    if key in ['scheduler', 'is_running']:
                        continue
                    if key.startswith('global') or key.startswith('tmp_') or key.startswith('_'):
                        continue
                    #logger.debug('Key:%s Value:%s', key, value)
                    if ModelSetting.get(key) != value:
                        change_list.append(key)
                        entity = F.db.session.query(ModelSetting).filter_by(key=key).with_for_update().first()
                        entity.value = value
                F.db.session.commit()
                return True, change_list 
            except Exception as e:
                logger.error(f"Exception:{str(e)}")
                logger.error(traceback.format_exc())
                logger.debug('Error Key:%s Value:%s', key, value)
                return False, []

        @staticmethod
        def get_list(key, delimeter='\n', comment='#'):
            value = None
            try:
                value = ModelSetting.get(key).replace('\n', delimeter)
                if comment is None:
                    values = [x.strip() for x in value.split(delimeter)]
                else:
                    values = [x.split(comment)[0].strip() for x in value.split(delimeter)]
                values = ModelSetting.get_list_except_empty(values)
                return values
            except Exception as e:
                logger.error(f"Exception:{str(e)}")
                logger.error(traceback.format_exc())
                logger.error('Error Key:%s Value:%s', key, value)


        @staticmethod
        def get_list_except_empty(source):
            tmp = []
            for _ in source:
                if _.strip().startswith('#'):
                    continue
                if _.strip() != '':
                    tmp.append(_.strip())
            return tmp

        @staticmethod
        def db_list_to_dict(db_list):
            ret = {}
            for item in db_list:
                ret[item.key] = item.value
            return ret

    return ModelSetting
