from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import json
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def salvar_cardapio(cardapio, cardapio_imagens):
    with open('cardapio.json', 'w') as f:
        json.dump(cardapio, f)
    with open('cardapio_imagens.json', 'w') as f:
        json.dump(cardapio_imagens, f)

def carregar_cardapio():
    try:
        with open('cardapio.json', 'r') as f:
            cardapio = json.load(f)
        with open('cardapio_imagens.json', 'r') as f:
            cardapio_imagens = json.load(f)
    except FileNotFoundError:
        cardapio = {}
        cardapio_imagens = {}
    return cardapio, cardapio_imagens

cardapio, cardapio_imagens = carregar_cardapio()

@app.route('/')
def index():
    is_admin = session.get('is_admin', False)
    return render_template('index.html', cardapio=cardapio, is_admin=is_admin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            session['is_admin'] = True
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos!')
    return render_template('login.html')

@app.route('/free_access', methods=['POST'])
def free_access():
    session['is_admin'] = False
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    return render_template('admin.html', cardapio=cardapio)

@app.route('/add', methods=['POST'])
def add_prato():
    if 'is_admin' in session and session['is_admin']:
        nome_prato = request.form['nome_prato']
        descricao = request.form['descricao']
        file = request.files['imagem']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            cardapio[nome_prato] = descricao
            cardapio_imagens[nome_prato] = filepath
            salvar_cardapio(cardapio, cardapio_imagens)
            flash('Prato adicionado com sucesso!')
        else:
            flash('Erro ao adicionar o prato.')
        return redirect(url_for('admin'))
    else:
        flash('Acesso negado.')
        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
