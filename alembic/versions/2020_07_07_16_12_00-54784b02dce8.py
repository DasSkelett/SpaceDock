"""Make default_version_id non-nullable

Revision ID: 54784b02dce8
Revises: 85be165bc5dc
Create Date: 2020-07-07 16:12:00.000000

"""
import sqlalchemy as sa

from alembic import op
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, orm, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

# revision identifiers, used by Alembic.
revision = '54784b02dce8'
down_revision = '85be165bc5dc'


Base = declarative_base()


class Mod(Base):
    __tablename__ = 'mod'
    id = Column(Integer, primary_key=True)
    default_version_id = Column(Integer, ForeignKey('modversion.id'))
    default_version = relationship('ModVersion',
                                   foreign_keys=default_version_id,
                                   post_update=True)


class ModVersion(Base):
    __tablename__ = 'modversion'
    id = Column(Integer, primary_key=True)
    mod_id = Column(Integer, ForeignKey('mod.id'))
    mod = relationship('Mod',
                       backref=backref('versions', order_by="desc(ModVersion.sort_index)"),
                       foreign_keys=mod_id)
    created = Column(DateTime, default=datetime.now)
    sort_index = Column(Integer, default=0)


class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    mod_id = Column(Integer, ForeignKey('mod.id'))
    mod = relationship('Mod', backref=backref('media', order_by=id))


class Featured(Base):
    __tablename__ = 'featured'
    id = Column(Integer, primary_key=True)
    mod_id = Column(Integer, ForeignKey('mod.id'))
    mod = relationship('Mod', backref=backref('featured', order_by=id))


def upgrade():
    # We have to make sure there are no mods without default_version left
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    for mod in session.query(Mod).filter_by(default_version_id=None).all():
        # This normally can't be. But if it is, just delete the mod, a mods without releases isn't worth much.
        if not mod.versions:
            session.delete(mod)
            for featured in session.query(Featured).filter(Featured.mod_id == mod.id).all():
                session.delete(featured)
            for media in session.query(Media).filter(Media.mod_id == mod.id).all():
                session.delete(media)
            for version in session.query(ModVersion).filter(ModVersion.mod_id == mod.id).all():
                session.delete(version)

        versions = sorted(mod.versions, key=lambda v: v.created)
        mod.default_version_id = versions[-1].id

    session.commit()

    # Now we can make the column non-nullable
    op.alter_column('mod', 'default_version_id',
                    existing_type=sa.INTEGER(),
                    nullable=False)


def downgrade():
    # Make the column nullable again
    op.alter_column('mod', 'default_version_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)
