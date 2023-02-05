from sqlalchemy.orm.session import Session
from schemas import UpdateConfig
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

    return db.query(DbConfig).filter(DbConfig.index == 1).first()

def update_config(request:UpdateConfig , db:Session):

    user = db.query(DbConfig).filter(DbConfig.user_id == user_id)
    user.update({
        DbConfig.name: request.name,
        DbConfig.lastname: request.lastname,
        DbConfig.photo: request.photo,
        DbConfig.phone_number: request.phone_number,
        DbConfig.email: request.email,
    })
    db.commit()

    return True