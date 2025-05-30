from flask import Blueprint
from .portfolio_calc import home


app = Blueprint("portfolio",__name__, template_folder="templates", url_prefix="/portfolio")
app.html_name = "חיזוי מניות"
app.description = "אתר שחוזה מניות\n מדובר על מחקר במתמטיקה תיאורטית בלבד (לא ייעוץ) שימוש בתוצאות באחריות המשתמש בלבד"
app.html_creator = "אליאור"
app.html_link = "https://www.facebook.com/elior.kinda"
app.html_img = "/static/elior.kinda.jpg"



@app.route('/')
def index():
    """Render the main game page."""
    return home()
    


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid common conflicts 
