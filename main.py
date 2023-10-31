import subprocess

subprocess.run("wget https://github.com/orcasgit/django-password-validation/raw/master/password_validation/common-passwords.txt.gz", shell=True)
subprocess.run("mv common-passwords.txt.gz /home/runner/.cache/pip/pool/94/b4/cf/", shell=True)
subprocess.run("python /home/runner/Resume-retool/manage.py migrate", shell=True)
subprocess.run("python /home/runner/Resume-retool/manage.py runserver 0.0.0.0:8000", shell=True)
subprocess.run("pwd", shell=True)

