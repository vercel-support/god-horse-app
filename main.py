from app import create_app

app = create_app()

if __name__ == '__main__':
    from uvicorn import run
    run('main:app', host='0.0.0.0', port=5000, workers=2)
