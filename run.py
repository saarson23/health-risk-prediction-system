# run.py - Application Entry Point
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("AI Health Risk Prediction System")
    print("Running at: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
