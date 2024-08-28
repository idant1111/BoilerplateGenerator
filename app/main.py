from flask import Flask, render_template, request, send_file, jsonify
import os
import yaml
import tempfile
import shutil

app = Flask(__name__)

def load_templates():
    templates = {}
    template_dir = 'language_templates'
    
    for language in os.listdir(template_dir):
        language_path = os.path.join(template_dir, language)
        if os.path.isdir(language_path):
            templates[language] = {}
            for filename in os.listdir(language_path):
                if filename.endswith('.yaml'):
                    project_type = filename[:-5]  # Remove .yaml extension
                    with open(os.path.join(language_path, filename), 'r') as file:
                        templates[language][project_type] = yaml.safe_load(file)
    return templates

templates = load_templates()

@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        language = request.form['language']
        project_type = request.form['project_type']
        project_name = request.form['project_name']
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = os.path.join(tmpdir, project_name)
            os.makedirs(project_path, exist_ok=True)
            
            # Get template structure
            template = templates.get(language, {}).get(project_type, {})            
            # Create directories and files
            for item, content in template.items():
                item_path = os.path.join(project_path, item)
                if isinstance(content, dict):
                    os.makedirs(item_path, exist_ok=True)
                    for subitem, subcontent in content.items():
                        subitem_path = os.path.join(item_path, subitem)
                        if isinstance(subcontent, dict):
                            os.makedirs(subitem_path, exist_ok=True)
                            for subsubitem, subsubcontent in subcontent.items():
                                subsubitem_path = os.path.join(subitem_path, subsubitem)
                                with open(subsubitem_path, 'w') as f:
                                    f.write(str(subsubcontent))  # Convert to string
                        else:
                            with open(subitem_path, 'w') as f:
                                f.write(str(subcontent))  # Convert to string
                else:
                    with open(item_path, 'w') as f:
                        f.write(str(content))  # Convert to string            
            # Add a README.md file
            readme_content = f"# {project_name}\n\nThis is a {language} {project_type} project generated using the Project Template Generator."
            with open(os.path.join(project_path, 'README.md'), 'w') as f:
                f.write(readme_content)
            
            # Create a zip file
            zip_path = os.path.join(tmpdir, f"{project_name}.zip")
            shutil.make_archive(zip_path[:-4], 'zip', project_path)
            
            return send_file(zip_path, as_attachment=True, download_name=f"{project_name}.zip")
    
    # Prepare language and project type options for the template
    options = {lang: list(projects.keys()) for lang, projects in templates.items()}
    return render_template('index.html', options=options)

@app.route('/api/options')
def get_options():
    options = {lang: list(projects.keys()) for lang, projects in templates.items()}
    return jsonify(options)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
