import app.utils.db_utils as u
from app.__init__ import create_app

app = create_app()


def main():
    u.enable_wal_mode()
    u.load_data()
    u.load_movielens_users()
    u.check_users_and_mappings()


if __name__ == "__main__":
    with app.app_context():
        main()