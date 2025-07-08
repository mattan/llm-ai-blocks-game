from flask import Blueprint
from .portfolio_calc import home, swot_home
from .portfolio_calc_summary import summarise_arbitrage



app = Blueprint("portfolio",__name__, template_folder="templates", url_prefix="/portfolio")
app.html_name = "חיזוי מניות"
app.description = "אתר שחוזה מניות\n מדובר על מחקר במתמטיקה תיאורטית בלבד (לא ייעוץ) שימוש בתוצאות באחריות המשתמש בלבד"
app.html_creator = "אליאור"
app.html_link = "https://www.facebook.com/elior.kinda"
app.html_img = "/static/elior.kinda.jpg"



@app.route('/')
def index():
    """דף נחיתה ראשי לקישורים שונים באפליקציית הפורטפוליו"""
    from flask import render_template
    return render_template('portfolio_index.html')

@app.route('/arbitrage')
def arbitrage():
    """הדף הישן של ניצול ארביטרג'"""
    return home()

@app.route('/arbitrage-summary')
def arbitrage_summary():
    """תצוגת סיכום ארביטראז' לפי כל זוג מניות שנשמרו בזיכרון"""
    from flask import render_template
    results = summarise_arbitrage()
    return render_template('arbitrage_summary.html', results=results)

@app.route('/swot')
def swot():
    return swot_home()
    


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid common conflicts 
