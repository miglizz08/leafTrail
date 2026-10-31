from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def dashboard(): 
    return render_template('dashboard.html')

@app.route('/novo-gasto', methods=['GET', 'POST'])
def novo_gasto():
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        valor = request.form.get('valor')
        categoria = request.form.get('categoria')
        data = request.form.get('data')

        print(f"Recebi: {descricao} | {valor} | {categoria} | {data}")

        return "Gasto cadastrado com sucesso!!"
    
    return render_template('novo_gasto.html')

if __name__ == "__main__":
    app.run(debug=True)
