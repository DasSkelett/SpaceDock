"""Clean up background image colums

Revision ID: 65d2acdcfbca
Revises: 73c9d707134b
Create Date: 2020-11-14 18:40:24.204786

"""

# revision identifiers, used by Alembic.
revision = '65d2acdcfbca'
down_revision = '73c9d707134b'

from alembic import op
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa


Base = declarative_base()


class ModList(Base):  # type: ignore
    __tablename__ = 'modlist'
    id = sa.Column(sa.Integer, primary_key=True)
    background = sa.Column(sa.String(512))


def upgrade() -> None:
    op.alter_column('modlist', 'background',
                    existing_type=sa.VARCHAR(length=32),
                    type_=sa.String(length=512),
                    existing_nullable=True)
    op.drop_column('game', 'bgOffsetY')
    op.drop_column('game', 'bgOffsetX')
    op.drop_column('mod', 'bgOffsetY')
    op.drop_column('mod', 'bgOffsetX')
    op.drop_column('modlist', 'bgOffsetY')
    op.drop_column('publisher', 'bgOffsetY')
    op.drop_column('publisher', 'bgOffsetX')
    op.drop_column('user', 'bgOffsetY')
    op.drop_column('user', 'bgOffsetX')


def downgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    for modlist in session.query(ModList).all():
        if modlist.background is not None and len(modlist.background) > 32:
            modlist.background = None

    session.commit()

    op.alter_column('modlist', 'background',
                    existing_type=sa.String(length=512),
                    type_=sa.VARCHAR(length=32),
                    existing_nullable=True)
    op.add_column('user', sa.Column('bgOffsetX', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('bgOffsetY', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('publisher', sa.Column('bgOffsetX', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('publisher', sa.Column('bgOffsetY', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('modlist', sa.Column('bgOffsetY', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('mod', sa.Column('bgOffsetX', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('mod', sa.Column('bgOffsetY', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('game', sa.Column('bgOffsetX', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('game', sa.Column('bgOffsetY', sa.INTEGER(), autoincrement=False, nullable=True))
