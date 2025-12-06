from app import app
from models.user_model import user_model

obj = user_model()


@app.route('/user/getall')
def user_getall_controller():
    return obj.user_getall_model()
