from flask import Flask, render_template, request, redirect,url_for
import json
import os
from types import SimpleNamespace
import re

app = Flask(__name__)
app.secret_key = 'proyecto_flask'


json_file_path = "data.json"

class Usuario:
    def __init__(self,id, correo, nombre, apellidos, contraseña, telefono, edad):
        self.id = id
        self.correo = correo
        self.nombre = nombre
        self.apellidos = apellidos
        self.contraseña = contraseña
        self.telefono = telefono
        self.edad = edad


def diccionario(d):
    keys = ['id', 'correo', 'nombre', 'apellidos', 'contraseña', 'telefono', 'edad']
    if all(key in d for key in keys):
     return Usuario(**d)
    else:
        return None
    
def cargar_usuario(file_path):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r") as json_file:
           content = json_file.read()
           if content:
               datos_cargados = json.loads(content, object_hook=diccionario)
               if datos_cargados:
                   return {'datos':datos_cargados}
    return{'datos':[]}     
     
def guardar_usuario(data):
    with open(json_file_path, "w") as json_file:
        json.dump(data['datos'], json_file, default=lambda o: o.__dict__, indent=2)


if os.path.exists(json_file_path) and os.path.getsize(json_file_path) > 0:
    data = cargar_usuario(json_file_path)
else:
    data = {'datos':[]}
        
id_counter = 1

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/enternew')
def enternew():
    return render_template('informacion.html')



@app.route('/insertar_datos', methods = ['GET','POST'])
def insertar_datos():
    if request.method == 'POST':
        global id_counter, data
        ce = request.form ['ce']
        nm = request.form ['nm'].title()
        ap = request.form ['ap'].title()
        psw = request.form ['psw']
        tlf = request.form ['tlf']
        ed = request.form ['ed']

        if not re.match("^[a-zA-Z\s]+$", nm) or not re.match("^[a-zA-Z\s]+$", ap):
            return render_template('resultado.html', msg = 'Debe Introducir solo letras')
        if len(tlf) > 15:
            return render_template('resultado.html', msg = 'Debe Tener una cantidad no mayor de 15 digitos')
        if len(psw) < 8:
            return render_template('resultado.html', msg = 'La Contraseña debe tener mas de 8 caracteres')
        if len(ed) > 2:
            return render_template('resultado.html', msg = 'La Edad no debe tener mas de 2 digitos')
        
        nuevo_dato= {
                   'id': id_counter,
                   'correo': ce,
                   'nombre': nm,
                   'apellidos': ap,
                   'contraseña': psw,
                   'telefono': tlf,
                   'edad': ed

        }
        while any(usuario.id == id_counter for usuario in data['datos']):
            id_counter += 1
        nuevo_dato['id'] = id_counter  
        id_counter += 1 
        
        data['datos'].append(Usuario(**nuevo_dato))

        guardar_usuario(data)        
          
    return redirect(url_for('list'))       
        
        
@app.route('/list')
def list():
    data = cargar_usuario(json_file_path)
    return render_template("list.html", rows=data['datos'])

@app.route("/edit", methods = ['GET','POST'])
def edit():
    if request.method == 'POST':
        id_editar = request.form.get('id')
        if id_editar is not None:
            for usuario in data['datos']:
                if usuario.id is not None and str(usuario.id) == id_editar:
                    id_usuario = int(usuario.id)
                    return render_template("edit.html", rows=[usuario])
    return redirect(url_for('list'))
     
@app.route("/editrec", methods=['POST','GET'])
def editrec():
        global data
        if request.method =="POST":
             id = request.form.get('id', '')
             ce = request.form.get('ce', '')
             nm = request.form.get('nm', '').title()
             ap = request.form.get('ap', '').title()
             psw = request.form.get('psw', '')
             tlf = request.form.get('tlf', '')
             ed = request.form.get('ed', '')

             if not re.match("^[a-zA-Z\s]+$", nm) or not re.match("^[a-zA-Z\s]+$", ap):
                return render_template('resultado.html', msg = 'Debe Introducir solo letras')  
             if len(tlf) > 15:
                return render_template('resultado.html', msg = 'Debe Tener una cantidad no mayor de 15 digitos')
             if len(psw) < 8:
                return render_template('resultado.html', msg = 'La Contraseña debe tener mas de 8 caracteres')
             if len(ed) > 2:
                return render_template('resultado.html', msg = 'La Edad no debe tener mas de 2 digitos')
             
             usuario = next((u for u in data['datos'] if str(u.id) == id), None)

             if usuario:
               usuario.correo = ce
               usuario.nombre = nm
               usuario.apellidos = ap
               usuario.contraseña = psw
               usuario.telefono = tlf
               usuario.edad = ed

                    
             
             with open(json_file_path, "w") as json_file:
                json.dump([u.__dict__ for u in data['datos']], json_file, indent=2)
             
        return render_template('resultado.html',msg = "Usuario Editado")                
             
         
@app.route('/delete', methods=['POST','GET'])
def delete():
    if request.method == 'POST':     
       global data
    id_borrar = request.form.get('id')
        
    usuario_eliminar = next((usuario for usuario in data['datos'] if str(usuario.id) == id_borrar), None)
        
    if usuario_eliminar:
        data['datos'].remove(usuario_eliminar)
        guardar_usuario(data)     
            
    return redirect(url_for('list'))

if __name__ == "__main__":
   app.run(debug=True)

