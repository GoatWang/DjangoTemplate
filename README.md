1. 建立虛擬環境，並啟動虛擬環境
    ```
    python -m virtualenv venv
    venv\Scripts\activate
    ```

2. 安裝套件:
    ```
    pip install -r requirements.txt
    ```
    如果psycopg2裝不起來，windows請去[這裡](https://www.lfd.uci.edu/~gohlke/pythonlibs/)下載wheel檔進行安裝，如果是linux請參考[這裡](http://initd.org/psycopg/docs/install.html)

3. 創建pwd.json檔案在DjangoTemplate目錄下，並輸入以下資訊
    ```
    {
        "db_name":"<要連接的資料庫名稱>",
        "db_user":"",
        "db_password":"",
        "db_host":"",
        "db_port":"5432",
        "smtp_host":"<寄申請帳號確認信件要使用的SMTP HOST>",
        "smtp_username":"",
        "smtp_password":""
        "smtp_from":"<記件信箱位置>" #例如: "XXXX有限公司<xxxx@gmail.com>"
    }
    ```    

4. 進去TPautomation資料夾=>設定初始資料庫=>創建superuser
    ```
    cd TPautomation
    python manage.py migrate
    python manage.py createsuperuser
    ```
5. 建立super user的First Name
    ```
    python manage.py shell
    >>> from django.contrib.auth.models import User
    >>> u = User.objects.get(pk=1)
    >>> u.first_name="<請自行輸入>"
    >>> u.save()
    ```

6. 啟動網頁
    ```
    python manage.py runserver
    ```


