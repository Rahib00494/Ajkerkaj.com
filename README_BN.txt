AJKERKAJ WEBSITE

চালানোর নিয়ম:
1) ZIP ফাইল Extract করুন।
2) কম্পিউটারে Python 3.10+ ইনস্টল থাকতে হবে।
3) এই ফোল্ডারে Terminal/CMD খুলুন।
4) চালান:
   python -m venv venv
   venv\\Scripts\\activate       (Windows)
   pip install -r requirements.txt
   python app.py
5) ব্রাউজারে খুলুন: http://127.0.0.1:5000

Admin:
URL: http://127.0.0.1:5000/admin/login
Username: admin
Password: admin123

নিরাপত্তা:
ইন্টারনেটে প্রকাশ করার আগে SECRET_KEY এবং ADMIN_PASSWORD environment variable দিয়ে বদলান।
Production-এ debug mode বন্ধ করুন এবং স্থায়ী database storage ব্যবহার করুন।
এই ZIP ফাইল নিজে থেকে public internet URL তৈরি করে না; Render/Python hosting-এ deploy করতে হবে।
