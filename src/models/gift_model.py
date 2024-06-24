from src.services import db


class Gift(db.Model):
    __tablename__ = "gift"

    code = db.Column("code", db.String(20), primary_key=True, nullable=False)
    was_used = db.Column("was_used", db.Boolean, nullable=False, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_attributes(self):
        return {
            "code": str(self.code),
            "was_used": self.was_used,
           }