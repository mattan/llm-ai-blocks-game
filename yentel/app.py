import os
from flask import Flask, render_template, Blueprint


app = Blueprint("yentel",__name__, template_folder="..", url_prefix="/yentel")
app.html_name = "ינטל הכרויות (החדש)"
app.html_creator = "הודיה"
app.html_link = "https://www.facebook.com/hodaya.netzer"
app.html_img = "https://scontent.ftlv20-2.fna.fbcdn.net/v/t39.30808-6/378677307_10227907340302787_7484898574107698310_n.jpg?_nc_cat=102&ccb=1-7&_nc_sid=6ee11a&_nc_eui2=AeF1Y6ZqxBtchauy0xJRvYjmueQ5s-CvPkG55Dmz4K8-QXtkfR9CYnFmPtLc5Tgdyio&_nc_ohc=uUTPZXfJUWgQ7kNvwHoy5iT&_nc_oc=AdnR3FiLlfL9fbWtQdQPBoUE_dyM7yqbZBm5XhBvLlSNZXVleHDOhFbiqQxovYW2gXUD8EVBkBjWahPsnssnrov9&_nc_zt=23&_nc_ht=scontent.ftlv20-2.fna&_nc_gid=aKRmPYOrgSxmGjlMhGkzlQ&oh=00_AfJqqKadg1lQUpqb66RgBg3ZFbOlapqh2UjkmkGuZM4qbA&oe=6823C937"



@app.route('/')
def index():
    """Render the main game page."""
    return render_template('yentel/templates/index.html')
    


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid common conflicts 
