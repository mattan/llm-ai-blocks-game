import os
from app import app as application 
application.run(debug=True,port=os.environ.get("PORT", 5000)) 