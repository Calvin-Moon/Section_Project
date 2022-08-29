from crypt import methods
from flask import Flask, request, render_template

import os
import time
import requests

from datetime import date, datetime, timezone, timedelta

#def schedulerJob():


# def backgroundScheduler():
#     scheduler = BackgroundScheduler(daemon=True)
#     scheduler.start()
#     scheduler.add_job(create_app.index, trigger='interval',seconds=10)

CSV_FILEPATH = os.path.join(os.getcwd(), __name__, 'df_model.csv') 

kamis_json = None
 
KST = timezone(timedelta(hours=9))
time_record = datetime.now(KST)
today = date.today()
yesterday = date.today() - timedelta(1)
weeksday = date.today() - timedelta(7)
        
t_day = today.strftime('%Y-%m-%d')
y_day = yesterday.strftime('%Y-%m-%d')
w_day = weeksday.strftime('%Y-%m-%d')

veg_list = {211:'배추', 231:'무', 232:'당근', 243:'붉은고추', 245:'양파', 258:'깐마늘(국산)'}
veg_list1 = {'배추':211, '무':231, '당근':232, '붉은고추':243, '양파':245, '깐마늘(국산)':258}
veg_list2 = {211:'cabbage', 231:'redish', 232:'carrot', 243:'pepper', 245:'onion', 258:'garlic'}
v_list = [211, 231, 232, 243, 245, 258]

vege_price = []


for list in v_list:
    response_kimchi = requests.get(f"http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&p_cert_key=0aefed54-a4ad-49ad-a839-29bb53dbecd6&p_cert_id=2703&p_returntype=json&p_startday={w_day}&p_endday={t_day}&p_itemcode={list}&p_convert_kg_yn=y&p_countrycode=1101&p_productclscode=02")
    kamis_kimchi = response_kimchi.json()
    kimchi_price = kamis_kimchi['data']['item'][-1]['price']
    k_price = float(kimchi_price.replace(',',''))
    vege_price.append(k_price)

cal = (vege_price[0]*2)+((vege_price[1]/20)*6)+(vege_price[2]/20)+(vege_price[3]/10)+(vege_price[4]/30)+(vege_price[5]/60)
make_kimchi = int(cal * 1.2)


def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        
        KST = timezone(timedelta(hours=9))
        time_record = datetime.now(KST)
        time_now = f'Time : {str(time_record.time())[:8]}'
        
        return render_template('index.html', kimchi=format(make_kimchi,','), today=t_day, nowtime=time_now)  
    

    @app.route('/json', methods = ['POST', 'GET'])
    def json_index():
        
        json_id = request.form['json_id']
        
        response = requests.get(f"http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&p_cert_key=0aefed54-a4ad-49ad-a839-29bb53dbecd6&p_cert_id=2703&p_returntype=json&p_startday={w_day}&p_endday={t_day}&p_itemcode={json_id}&p_convert_kg_yn=y&p_countrycode=1101&p_productclscode=02")
        kamis_json = response.json()
        
        veg_name = f"{kamis_json['data']['item'][-1]['itemname']} 의 JSON 데이터"
        KST = timezone(timedelta(hours=9))
        time_record = datetime.now(KST)
        time_now = f'Time : {str(time_record.time())[:8]}'
        
        return render_template('index.html', jsonname=veg_name, json_data=kamis_json,kimchi=format(make_kimchi,','), today=t_day, nowtime=time_now)
                
        # return f"{veg_name} 의 최근 주간 판매가격 정보입니다: {kamis_json}"
        

    @app.route('/product',defaults={'product_id' : 211})
    @app.route('/product/<int:product_id>')
    def input_index(product_id):

        response = requests.get(f"http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&p_cert_key=0aefed54-a4ad-49ad-a839-29bb53dbecd6&p_cert_id=2703&p_returntype=json&p_startday={w_day}&p_endday={t_day}&p_itemcode={product_id}&p_convert_kg_yn=y&p_countrycode=1101&p_productclscode=02")
        kamis_json_product = response.json()
        
        if response.status_code == 200:
            kamis_json_product = response.json()

        t_price_product = kamis_json_product['data']['item'][-1]['price']
        result = f"{t_day} {veg_list[product_id]} 가격은 {t_price_product}원 입니다"

        return result


    @app.route('/product_name/', defaults={'p_name' : '배추'})
    @app.route('/product_name/<p_name>')
    def name_index(p_name):

        response = requests.get(f"http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&p_cert_key=0aefed54-a4ad-49ad-a839-29bb53dbecd6&p_cert_id=2703&p_returntype=json&p_startday={w_day}&p_endday={t_day}&p_itemcode={veg_list1[p_name]}&p_convert_kg_yn=y&p_countrycode=1101&p_productclscode=02")
        
        if response.status_code == 200:
            kamis_json = response.json()

        t_price = kamis_json['data']['item'][-1]['price']
        result = f"{t_day} {p_name} {veg_list1[p_name]} 가격은 {t_price}원 입니다"

        return result
    
    @app.route('/pro', methods = ['POST', 'GET'])
    def html_index():

        #request.method == 'GET'
        product_id = request.form['id'] or request.form['pred_id']
        
        response = requests.get(f"http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&p_cert_key=0aefed54-a4ad-49ad-a839-29bb53dbecd6&p_cert_id=2703&p_returntype=json&p_startday={w_day}&p_endday={t_day}&p_itemcode={product_id}&p_convert_kg_yn=y&p_countrycode=1101&p_productclscode=02")
        
        kamis_json_pro = response.json()
        
        if response.status_code == 200:
            kamis_json_pro = response.json()

        t_price_pro = kamis_json_pro['data']['item'][-1]['price']
        kind_name = kamis_json_pro['data']['item'][-1]['kindname']
        item_name = kamis_json_pro['data']['item'][-1]['itemname']
        
        KST = timezone(timedelta(hours=9))
        time_record = datetime.now(KST)
        time_now = f'Time : {str(time_record.time())[:8]}'

        return render_template('index.html', price=f"{t_price_pro}원", kindname=kind_name, itemname=item_name, kimchi=format(make_kimchi,','), today=t_day, nowtime=time_now)
    
    
    @app.route('/predict', methods = ['POST', 'GET'])
    def predict():
 
 
        p_id = request.form['pred_id']
        p_temp = request.form['temp']
        p_rain = request.form['rain']
        p_hum = request.form['hum']
        p_sun = request.form['sun']
        
        input_data = f"기온 : {p_temp} 도 , 강수량 : {p_rain} mm , 습도 : {p_hum} % , 일조량 : {p_sun} 시간"
        
        response = requests.get(f"http://www.kamis.or.kr/service/price/xml.do?action=periodProductList&p_cert_key=0aefed54-a4ad-49ad-a839-29bb53dbecd6&p_cert_id=2703&p_returntype=json&p_startday={w_day}&p_endday={t_day}&p_itemcode={p_id}&p_convert_kg_yn=y&p_countrycode=1101&p_productclscode=02")
        kamis_json_pro = response.json()
        
        t_price_pro = kamis_json_pro['data']['item'][-1]['price']
        kind_name = kamis_json_pro['data']['item'][-1]['kindname']
        item_name = kamis_json_pro['data']['item'][-1]['itemname']
        
        KST = timezone(timedelta(hours=9))
        time_record = datetime.now(KST)
        time_now = f'Time : {str(time_record.time())[:8]}'
        
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LinearRegression


        # model = None
        # with open('/Users/chulyoungmoon/Section3/s3_project/myproject/flask_app/model_cabbage.pkl','rb') as pickle_file:
        #     model = pickle.load(pickle_file)
        
        p_id = int(p_id)
        X_test = []
        target = veg_list2[p_id]
        features = ['temperature','rainfall','humidity', 'total_sun']
        
        df_model = pd.read_csv(CSV_FILEPATH)

        # X_test = pd.DataFrame({'temperature':0, 'rainfall':0, 'humidity':0, 'total_sun':0 })
        # X_test.loc[0] = [p_temp, p_rain, p_hum, p_sun]
        
        
        X_train, X_test, y_train, y_test = train_test_split(df_model[features], df_model[target], random_state=42)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
                
        X_test = [float(p_temp), float(p_rain), float(p_hum), float(p_sun)]
        y_pred = int(model.predict([X_test]))
    
        # return render_template('index.html', pred_price=int(y_pred[0]), kindname=kind_name, itemname=item_name)
        return render_template('index.html', pred_price=f"{format(y_pred,',')}원", price=f"{t_price_pro}원", kindname=kind_name, itemname=item_name, input=input_data, kimchi=format(make_kimchi,','), today=t_day, nowtime=time_now)

    # scheduler = BackgroundScheduler(daemon=True)
    # scheduler.start()
    # scheduler.add_job(index, trigger='interval',seconds=10)

    return app

# if __name__ == "__main__":
#     app.run(debug=True)

# schedule.every(10).seconds.do(create_app)

# while True:
#     schedule.run_pending()
#     time.sleep(1)