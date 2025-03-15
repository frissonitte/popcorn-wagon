"""Review function and action tracking removed. User - tag relations improved for algorithm

Revision ID: 990d21987871
Revises: f750fa7899a4
Create Date: 2025-03-15 16:03:42.298557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '990d21987871'
down_revision = 'f750fa7899a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_movie_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tagId', sa.Integer(), nullable=True))
        batch_op.create_index('idx_user_movie_data_movieId', ['movieId'], unique=False)
        batch_op.create_index('idx_user_movie_data_userId', ['userId'], unique=False)
        batch_op.create_foreign_key('fk_user_movie_data_tagId', 'tags', ['tagId'], ['id'])
        batch_op.drop_column('action')
        batch_op.drop_column('review')


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_movie_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('review', sa.VARCHAR(length=255), nullable=True))
        batch_op.add_column(sa.Column('action', sa.VARCHAR(length=8), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index('idx_user_movie_data_userId')
        batch_op.drop_index('idx_user_movie_data_movieId')
        batch_op.drop_column('tagId')

    # ### end Alembic commands ###
