from flask import Flask, render_template, request, redirect, url_for, session
import math
import os

app = Flask(__name__)
# secret key for session storage; use env var in production
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')


def load_favorites():
    return session.get('favorites', [])


def save_favorites(favs):
    session['favorites'] = favs


@app.route('/', methods=['GET', 'POST'])
def index():
    pj = None
    var_ticker = ''
    vpa_str = ''
    lpa_str = ''
    favorited = False
    favorites = load_favorites()
    if request.method == 'POST':
        var_ticker = request.form.get('ticker', '').strip().upper()
        vpa_str = request.form.get('vpa', '').replace(',', '.').strip()
        lpa_str = request.form.get('lpa', '').replace(',', '.').strip()
        try:
            vpa = float(vpa_str) if vpa_str else 0.0
            lpa = float(lpa_str) if lpa_str else 0.0
            pj = math.sqrt(22.5 * vpa * lpa)
        except ValueError:
            pj = None

        # se pediu favoritar, salva/atualiza em favorites.json
        if pj is not None and request.form.get('favorite'):
            found = False
            pj_rounded = round(pj, 2)
            for item in favorites:
                if item.get('ticker', '').upper() == var_ticker:
                    item['price'] = pj_rounded
                    found = True
                    break
            if not found:
                favorites.append({'ticker': var_ticker, 'price': pj_rounded})
            save_favorites(favorites)
            favorites = load_favorites()

        # set favorited flag after processing
        favorited = any(item.get('ticker', '').upper() == var_ticker for item in favorites) if var_ticker else False

    return render_template('index.html', result=pj, name_ticker=var_ticker, favorites=favorites, vpa=vpa_str, lpa=lpa_str, favorited=favorited)


@app.route('/remove', methods=['POST'])
def remove_favorite():
    ticker = request.form.get('ticker', '').strip().upper()
    favorites = load_favorites()
    favorites = [f for f in favorites if f.get('ticker', '').upper() != ticker]
    save_favorites(favorites)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)