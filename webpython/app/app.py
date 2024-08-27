from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Kunci rahasia untuk session
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Simpan data awal dalam config
app.config['TITLE'] = "SELAMAT DATANG DI SMK TELEKOMUNIKASI TELESANDI BEKASI"
app.config['SUBTITLE'] = "\"We Are Not The Best, But We Want To Be Excellent\""
app.config['IMAGE'] = "vector-header.png"

data_jurusan = {
    1: {
        "nama": "Rekayasa Perangkat Lunak",
        "skills": [
            "Perancangan System", 
            "Database", 
            "Pemrograman Berorientasi Objek", 
            "Pemrograman Web dan Mobile"
        ],
        "image": "rpl.jpg"
    },
    2: {
        "nama": "Teknik Komputer dan Jaringan",
        "skills": [
            "Teknologi Jaringan Berbasis Luas", 
            "Administrasi Infrastruktur Jaringan", 
            "Administrasi Sistem Jaringan", 
            "Teknologi Layanan Jaringan"
        ],
        "image": "tkj2.jpg"
    },
    3: {
        "nama": "Desain Komunikasi Visual",
        "skills": [
            "Desain Grafis Percetakan", 
            "Desain Media Interaktif", 
            "Teknik Animasi 2D dan 3D", 
            "Teknik Pengolahan Audio & Video"
        ],
        "image": "dkv.jpg"
    },
    4: {
        "nama": "Teknik Transmisi Telekomunikasi",
        "skills": [
            "Dasar Sistem Telekomunikasi", 
            "Elektronika dan Microcontroller", 
            "Transmisi Satelit [VSAT.IP]", 
            "Transmisi Radio [BTS]"
        ],
        "image": "telko.jpg"
    },
}

# Definisi username dan password admin
admin_username = 'admin'
admin_password = '123'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/')
def home():
    title = app.config.get('TITLE')
    subtitle = app.config.get('SUBTITLE')
    image = app.config.get('IMAGE')
    return render_template('index.html', title=title, subtitle=subtitle, image_filename=image, active_page='home', admin_logged_in=session.get('admin'))

@app.route('/about')
def about():
    return render_template('about.html', active_page='about', admin_logged_in=session.get('admin'))

@app.route('/countac')
def countac():
    return render_template('countac.html', active_page='countac', admin_logged_in=session.get('admin'))

@app.route('/jurusan')
def jurusan():
    return render_template('jurusan.html', data_jurusan=data_jurusan, active_page='jurusan', admin_logged_in=session.get('admin'))

@app.route('/kelola', methods=['GET', 'POST'])
def kelolahome():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)
                app.config['IMAGE'] = image_filename
        
        app.config['TITLE'] = title
        app.config['SUBTITLE'] = subtitle

        return redirect(url_for('home'))
    
    return render_template('kelolahome.html', title=app.config['TITLE'], subtitle=app.config['SUBTITLE'], active_page='kelolahome', admin_logged_in=session.get('admin'))

@app.route('/kelolajurusan', methods=['GET'])
def kelolajurusan():
    return render_template(
        'kelolajurusan.html', 
        data_jurusan=data_jurusan, 
        active_page='kelolajurusan', 
        admin_logged_in=session.get('admin')
    )

@app.route('/update_jurusan', methods=['POST'])
def update_jurusan():
    global data_jurusan
    for id in data_jurusan.keys():
        nama = request.form.get(f'nama{id}')
        skills = request.form.get(f'skills{id}').split(', ')
        image = request.files.get(f'image{id}')
        
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image_path = os.path.join('static/image', image_filename)
            image.save(image_path)
        else:
            image_filename = data_jurusan[id]['image']
        
        data_jurusan[id] = {
            "nama": nama,
            "skills": skills,
            "image": image_filename
        }
    
    return redirect(url_for('kelolajurusan'))

@app.route('/dasboard')
def dasboardadmin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    return render_template('dasboardadmin.html', active_page='dasboardadmin', admin_logged_in=session.get('admin'))

@app.route('/login', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username dan password harus diisi!', 'error')
            return redirect(url_for('login'))
        
        if username == admin_username and password == admin_password:
            session['admin'] = True
            flash('Login berhasil!', 'success')
            return redirect(url_for('dasboardadmin'))
        else:
            flash('Username atau password salah!', 'error')
            return redirect(url_for('login'))
    
    return render_template('adminlogin.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists('static/image'):
        os.makedirs('static/image')
    app.run(debug=True)
