from flask import render_template
from app import app, db

# global helper that turns a collection of errors into an error string
def error_str(error_list, label="error(s): "):
    return reduce(lambda x, y: x + y, error_list, label)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
