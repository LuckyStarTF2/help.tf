from app import helptf


@helptf.route('/')
@helptf.route('/index')
def index():
    return "ffs"
