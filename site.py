from flask import Flask, render_template
app = Flask(__name__)

# Define CSS style
def css():
    return """
<style>
body {
    background-color: #f0f0f0; /*  */
    font-family: Arial, sans-serif;
}
</style>
"""

# HTML content
def html_content(css):
    css += "\n"
    return '''
<html>
<head><title>New Page</title></head>
<body>
<div style="background-color: #f0f0f0; font-family: 
Arial, sans-serif;">
   <h1>Heading with CSS styling</h1>
</div>
</html>
'''

# Create a response from the HTML content and CSS
def create_response(css):
    html_content = html_content(css)
    css_style = '<style>' + css() + '</style>'
    return '''<div 
class="container">'''.format(css())

@app.route('/')
def index():
    return render_template('index.html', css=css,
html_content=html_content)

# Example usage of HTML content and CSS style
if __name__ == '__main__':
    app.run(render_template('index.html'), 100)
