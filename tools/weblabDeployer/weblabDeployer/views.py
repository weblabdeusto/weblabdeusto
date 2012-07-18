from weblabDeployer import app

@app.route('/')
def index():
    return render_template('base.html')