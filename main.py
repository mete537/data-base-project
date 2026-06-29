# Kütüphaneleri yükleme/Flask'a bağlanma
from flask import Flask, render_template, request, redirect, session
# Veti tabanı kütüphanesine bağlanma
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
# Oturum için gizli anahtarın ayarlanması
app.secret_key = 'my_top_secret_123'

# instance klasörünü oluştur
instance_path = os.path.join(os.path.dirname(__file__), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# SQLite bağlantısı kurma (absolute path)
db_path = os.path.join(instance_path, 'diary.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Veritabanı oluşturma
db = SQLAlchemy(app)
# Tablo oluşturma

class Card(db.Model):
    # Tablo giriş alanları oluşturma
    # id
    id = db.Column(db.Integer, primary_key=True)
    # Başlık
    title = db.Column(db.String(100), nullable=False)
    # Alt başlık
    subtitle = db.Column(db.String(300), nullable=False)
    # Metin
    text = db.Column(db.String, nullable=False)
    # Kart sahibinin e-posta adresi
    user_email = db.Column(db.String(100), nullable=False)

    # Nesneyi ve kimliğini çıktı olarak verme
    def __repr__(self):
        return f'<Card {self.id}>'
    

# Görev #1. Kullanıcı tablosunu oluşturun.
class User(db.Model):
    # Sütunları oluşturma
    # kimlik
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    theme = db.Column(db.String, default='dark')  # Tema ayarı
    notifications = db.Column(db.Boolean, default=True)  # Bildirim ayarı

    def __repr__(self):
        return f'<User {self.id}>'

# İçerik sayfasını başlatma
@app.route('/', methods=['GET','POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']
            
        # Görev #4. Kullanıcı doğrulamasını uygulayın
        user = User.query.filter_by(email=form_login).first()
        if user and user.password == form_password:
            session['user_email'] = user.email
            return redirect('/index')
        else:
            error = 'Yanlış kullanıcı adı veya şifre'
    
    return render_template('login.html', error=error)
      
@app.route('/reg', methods=['GET','POST'])
def reg():
    error = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form.get('password_confirm', '')
        
        # Şifreyi doğrulama
        if password != password_confirm:
            error = 'Şifreler uyuşmuyor'
            return render_template('registration.html', error=error)
        
        # Email zaten kayıtlı mı kontrol et
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error = 'Bu e-posta zaten kayıtlı'
            return render_template('registration.html', error=error)
        
        # Görev #3. Kullanıcı doğrulamasını uygulayın
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        
        return redirect('/')
    
    return render_template('registration.html', error=error)


# Çıkış
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# İçerik sayfasını başlatma
@app.route('/index')
def index():
    if 'user_email' not in session:
        return redirect('/')
    
    # Görev #4. Kullanıcının yalnızca kendi kartlarını görmesini sağlayın.
    cards = Card.query.filter_by(user_email=session['user_email']).order_by(Card.id).all()
    return render_template('index.html', cards=cards)

# Kart sayfasını başlatma
@app.route('/card/<int:id>')
def card(id):
    if 'user_email' not in session:
        return redirect('/')
    
    card = Card.query.get(id)
    if not card or card.user_email != session['user_email']:
        return redirect('/index')
    
    return render_template('card.html', card=card)

# Kart oluşturma sayfasını başlatma
@app.route('/create')
def create():
    if 'user_email' not in session:
        return redirect('/')
    
    return render_template('create_card.html')

# Kart formu
@app.route('/form_create', methods=['GET','POST'])
def form_create():
    if 'user_email' not in session:
        return redirect('/')
    
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']

        # Görev #4. Kullanıcı adına kart oluşturma işlemini gerçekleştirin.
        card = Card(title=title, subtitle=subtitle, text=text, user_email=session['user_email'])

        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    
    return render_template('create_card.html')


# Ayarlar/Özelleştirme sayfası
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_email' not in session:
        return redirect('/')
    
    user = User.query.filter_by(email=session['user_email']).first()
    message = ''
    
    if request.method == 'POST':
        # Tema ayarı
        if 'theme' in request.form:
            user.theme = request.form['theme']
        
        # Bildirim ayarı
        user.notifications = 'notifications' in request.form
        
        db.session.commit()
        message = 'Ayarlar başarıyla güncellendi'
    
    return render_template('settings.html', user=user, message=message)

# Tabloları oluştur
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
