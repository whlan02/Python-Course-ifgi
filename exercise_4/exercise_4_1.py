# Import required modules
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWebKitWidgets import QWebView

# Create the Wikipedia URL using the district name
wiki_url = f"https://en.wikipedia.org/wiki/[%Name%]"

# Create a QWebView instance
web_view = QWebView()

# Load the URL into the web view
web_view.load(QUrl(wiki_url))

# Show the web view window
web_view.show()
