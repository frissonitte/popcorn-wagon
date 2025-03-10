"""Initial migration.

Revision ID: 815f081725e5
Revises: 
Create Date: 2025-03-10 14:22:43.487136

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '815f081725e5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('movies',
    sa.Column('movieId', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('genres', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('movieId')
    )
    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.create_index('idx_movie_title', ['title'], unique=False)

    op.create_table('users',
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('hash', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('userId'),
    sa.UniqueConstraint('username')
    )
    op.create_table('links',
    sa.Column('movieId', sa.Integer(), nullable=False),
    sa.Column('imdbId', sa.Integer(), nullable=True),
    sa.Column('tmdbId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['movieId'], ['movies.movieId'], ),
    sa.PrimaryKeyConstraint('movieId')
    )
    op.create_table('ratings',
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('movieId', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.Integer(), nullable=False),
    sa.Column('rating', sa.REAL(), nullable=False),
    sa.ForeignKeyConstraint(['movieId'], ['movies.movieId'], ),
    sa.ForeignKeyConstraint(['userId'], ['users.userId'], ),
    sa.PrimaryKeyConstraint('userId', 'movieId')
    )
    with op.batch_alter_table('ratings', schema=None) as batch_op:
        batch_op.create_index('idx_rating_movieId', ['movieId'], unique=False)
        batch_op.create_index('idx_rating_userId', ['userId'], unique=False)

    op.create_table('tags',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('movieId', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['movieId'], ['movies.movieId'], ),
    sa.ForeignKeyConstraint(['userId'], ['users.userId'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('userId', 'movieId', 'tag', name='unique_user_movie_tag')
    )
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.create_index('idx_tag_tag', ['tag'], unique=False)
        batch_op.create_index('idx_tag_user_movie', ['userId', 'movieId'], unique=False)

    op.create_table('user_lists',
    sa.Column('listId', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('list_name', sa.String(length=100), nullable=False),
    sa.Column('timestamp', sa.TIMESTAMP(), nullable=True),
    sa.Column('background_image', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['userId'], ['users.userId'], ),
    sa.PrimaryKeyConstraint('listId')
    )
    op.create_table('user_mapping',
    sa.Column('movielens_userId', sa.Integer(), nullable=False),
    sa.Column('system_userId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['system_userId'], ['users.userId'], ),
    sa.PrimaryKeyConstraint('movielens_userId'),
    sa.UniqueConstraint('system_userId')
    )
    op.create_table('user_movie_data',
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('movieId', sa.Integer(), nullable=False),
    sa.Column('action', sa.Enum('RATED', 'REVIEWED', 'WATCHED', name='useraction'), nullable=False),
    sa.Column('liked', sa.Boolean(), nullable=False),
    sa.Column('rating', sa.REAL(), nullable=False),
    sa.Column('review', sa.String(length=255), nullable=True),
    sa.CheckConstraint('liked IN (-1, 0, 1)', name='liked_check'),
    sa.CheckConstraint('rating BETWEEN 1 AND 10', name='rating_check'),
    sa.ForeignKeyConstraint(['movieId'], ['movies.movieId'], ),
    sa.ForeignKeyConstraint(['userId'], ['users.userId'], ),
    sa.PrimaryKeyConstraint('userId', 'movieId', 'action', name='primary_key_constraint')
    )
    op.create_table('user_list_items',
    sa.Column('itemId', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('listId', sa.Integer(), nullable=False),
    sa.Column('movieId', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['listId'], ['user_lists.listId'], ),
    sa.ForeignKeyConstraint(['movieId'], ['movies.movieId'], ),
    sa.ForeignKeyConstraint(['userId'], ['users.userId'], ),
    sa.PrimaryKeyConstraint('itemId'),
    sa.UniqueConstraint('listId', 'movieId', name='unique_list_movie')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_list_items')
    op.drop_table('user_movie_data')
    op.drop_table('user_mapping')
    op.drop_table('user_lists')
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.drop_index('idx_tag_user_movie')
        batch_op.drop_index('idx_tag_tag')

    op.drop_table('tags')
    with op.batch_alter_table('ratings', schema=None) as batch_op:
        batch_op.drop_index('idx_rating_userId')
        batch_op.drop_index('idx_rating_movieId')

    op.drop_table('ratings')
    op.drop_table('links')
    op.drop_table('users')
    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.drop_index('idx_movie_title')

    op.drop_table('movies')
    # ### end Alembic commands ###
