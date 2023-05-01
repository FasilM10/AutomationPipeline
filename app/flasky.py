import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)

#if __name__ == '__main__':
#    app.run(debug=False,host='0.0.0.0',port=5000)

#$env:FLASK_APP = "flasky.py"