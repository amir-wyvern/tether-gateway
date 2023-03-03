from sqlalchemy.orm.session import Session
from db.models import DbConfig

def init_table(db:Session):

    data = get_config(db)
    if data is None:
        config = DbConfig()
        db.add(config)
        db.commit()
        db.refresh(config)

        return config

def get_config(db:Session):
    resp = db.query(DbConfig).filter(DbConfig.index == 1).first()
    return resp

