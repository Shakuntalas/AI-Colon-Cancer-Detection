from app import create_app
from app.extensions import db

def test_factory():
    try:
        app = create_app('testing')
        with app.app_context():
            db.create_all()
        print("Application factory initialized and database tables created successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_factory()
