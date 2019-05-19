# Stock Bridge

Keeping in view the real thrill of the market monotony, we are here with the Virtual Simulation of the same thrill and adrenaline rush through the event under the banner of **Morphosis'19, NIT Mizoram**. The virtual share market enables the participants to trade, buy, sell mortgage and showcase their rationality, their mettle against competitive decision making under pressure. The full time active virtual market will be a platform to showcase your inferential, pressure-handling capability.

## Instructions for setting up the project

1. Clone the repository  
   `git clone https://github.com/morphosis-nitmz/Stock-Bridge/tree/heroku`

2. Rename the file **.env-sample** to **.env** and replace the value of `SECRET_KEY` with the secret key of your own project. To generate a new secret key

   - Go to terminal and create a new django project `django-admin startproject <proj-name>`.
   - Now get the value of `SECRET_KEY` in _settings.py_ and use that as the secret key for the **Stock-Bridge project**.
   - Now delete that new django project.

3. **Sendgrid setup**:
   - Create an account on [sendgrid](https://sendgrid.com/).
   - Add your sendgrid username and password to `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in **.env** respectively.
   - Change the email and name in `DEFAULT_FROM_EMAIL` and `MANAGERS` in all _settings files_ with your name and email.
