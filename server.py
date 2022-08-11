from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime
import hashlib
import os
#import dotenv
#from os.path import join, dirname
#from dotenv import load_dotenv
import random
from num2words import num2words

#from flask_sslify import SSLify

app = Flask(__name__, template_folder='templates')
#sslify = SSLify(app)

# GLOBAL
SITE_URL = "dice-rolly.glitch.me"
      
# indexes for toss_coin() return
RAW_TOSSES = 0
HEADS_TOTAL = 1
TAILS_TOTAL = 2
EDGE_TOTAL = 3

# indexes for roll_dice() return
RAW_ROLLS = 0
ROLL_TOTAL = 1

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.route("/", methods=["GET"])
def homepage():
  #return 'hello'
  return render_template("index.html",
                        show_all_tiles=True)

@app.route("/dice/", methods=["GET"])
def dicepage():
  #return 'hello'
  return render_template("index.html",
                        show_dice_tiles=True)

@app.route("/coin/", methods=["GET"])
def coinpage():
  #return 'hello'
  return render_template("index.html",
                        show_coin_tiles=True)

# roll dice home
@app.route("/roll-dice/", methods=["GET"])
def roll_dice_single_page():
       
    dice_roll = roll_dice(1, 6)
    roll = dice_roll[RAW_ROLLS][0]

    return render_template("roll.html",
                           single_roll = roll,
                           timestamp = get_timestamp(),
                           roll_type = 'roll-dice-home')
      
# toss coin home
@app.route("/toss-coin/", methods=["GET", "POST"])
def toss_coin_page():
    
    coin_toss = toss_coin()
    toss = coin_toss[RAW_TOSSES][0]
        
    return render_template("roll.html",
                           single_toss = toss,
                           timestamp = get_timestamp(),
                           roll_type = 'toss-coin-home')
  
# magic 8 ball home
@app.route("/magic-8-ball/", methods=["GET"])
def magic_8_ball_page():

    message = shake_8_ball()
    return render_template("roll.html",
                           page_message = message,
                           timestamp = get_timestamp(),
                           roll_type = 'magic-8-ball')

# six-sided dice
@app.route("/roll-dice/six-sided/", methods=["GET"])
@app.route("/roll-dice/six-sided/<int:dice_quantity>/", methods=["GET"])
def six_sided_dice_roll_page(dice_quantity=1):
  
    if dice_quantity not in range(1,1001):
      return render_template('message.html',
                             page_title_suffix = ' - Error',
                             page_img_src = '/static/icon.svg',
                             page_headline = 'Invalid dice count',
                             page_message = 'Please enter a number between 1 and 1000.')
  
    else:
        dice_roll = roll_dice(dice_quantity, 6)        
        return render_template("roll.html",
                               page_roll_count = dice_quantity,
                               page_dice_type = num2words(6),
                               page_roll_list = dice_roll[RAW_ROLLS],
                               page_roll_total = dice_roll[ROLL_TOTAL],
                               timestamp = get_timestamp(),
                               roll_type = 'six-sided-dice')
      
# twelve-sided dice
@app.route("/roll-dice/twelve-sided/", methods=["GET"])
@app.route("/roll-dice/twelve-sided/<int:dice_quantity>/", methods=["GET"])
def twelve_sided_dice_roll_page(dice_quantity=1):

    if dice_quantity not in range(1,1001):
      return render_template('message.html',
                             page_title_suffix = ' - Error',
                             page_img_src = '/static/icon.svg',
                             page_headline = 'Invalid dice count',
                             page_message = 'Please enter a number between 1 and 1000.')
    
    else:
        dice_roll = roll_dice(dice_quantity, 12)      
        return render_template("roll.html",
                               page_roll_count = dice_quantity,
                               page_dice_type = num2words(12),
                               page_roll_list = dice_roll[RAW_ROLLS],
                               page_roll_total = dice_roll[ROLL_TOTAL],
                               timestamp = get_timestamp(),
                               roll_type = 'twelve-sided-dice')

# custom dice page
@app.route("/roll-dice/custom/", methods=["GET", "POST"])
def custom_dice_form_page(dice_quantity=1, dice_type=6):

    if request.method == "GET":
        return render_template('form.html',
                               page_title_suffix = " - Custom Dice Roll",
                               form='custom-dice')

    elif request.method == "POST":
      
        dice_type = request.form["dice-type"]
        number_of_dice = request.form["no-of-dice"]
        
        # NEEDS WORK - breaks ssl
        return redirect(f"/roll-dice/{dice_type}/{number_of_dice}")

# custom dice-page roll
@app.route("/roll-dice/<int:dice_type>-sided/<int:dice_quantity>/", methods=["GET"])
def custom_dice_roll_page(dice_quantity=1, dice_type=6):
  
    if dice_quantity not in range(1,1000):
      return render_template('message.html',
                             page_title_suffix = 'Error',
                             page_img_src = '/static/icon.svg',
                             page_headline = 'Invalid dice count',
                             page_message = 'Please enter a number between 1 and 1000.')
    
    else:
        dice_roll = roll_dice(dice_quantity,dice_type)
        
        return render_template("roll.html",
                               page_title_suffix = " - Custom Dice",
                               page_roll_count = dice_quantity,
                               page_dice_type = num2words(dice_type),
                               page_roll_list = dice_roll[RAW_ROLLS],
                               page_roll_total = dice_roll[ROLL_TOTAL],
                               timestamp = get_timestamp(),
                               roll_type = 'custom-dice')

# custom coin toss form
@app.route("/toss-coin/custom/", methods=["GET", "POST"])
def toss_coin_custom_page():

    if request.method == "GET":
        return render_template('form.html',
                               page_title_suffix = " - Custom Coin Toss",
                               form='custom-coin-toss')

    elif request.method == "POST":
        
        toss_type = request.form["toss-type"]
        number_of_times_coin_toss = request.form["number-of-times-coin-toss"]
        
        if toss_type == 'no-edge':
            # NEEDS WORK - breaks ssl
            return redirect(f"/toss-coin/no-edge/{number_of_times_coin_toss}/")
          
        elif toss_type == 'with-edge':
            # NEEDS WORK - breaks ssl
            return redirect(f"/toss-coin/with-edge/{number_of_times_coin_toss}/")
          
# random numbers form
@app.route("/random-numbers/", methods=["GET", "POST"])
def rng_form_page():

    if request.method == "GET":
        return render_template('form.html',
                               page_title_suffix = " - Random Number Generator",
                               form='rng')

    elif request.method == "POST":        
        number_min = int(request.form["number-min"])
        number_max = int(request.form["number-max"])
        number_qty = int(request.form["number-qty"])
        allow_dupes_str = request.form["allow-dupes"]
        sort = request.form["sort-method"]
        add_commas_str = request.form["add-commas"]

        if allow_dupes_str == "True":
            allow_dupes = True
        else:
            allow_dupes = False

        if add_commas_str == "True":
            add_commas = True
        else:
            add_commas = False      

        errors = check_errors(number_min, number_max, number_qty, allow_dupes)
        if errors == None:
            number_list = []
            number_list = generate_numbers(number_min, number_max, number_qty, allow_dupes, sort, add_commas)
        
            return render_template("roll.html",
                            page_title_suffix = ' - Random Number Generator',
                            numbers = number_list,
                            timestamp = get_timestamp(),
                            roll_type = 'rng')
        else:
            return render_template('message.html',
                        page_title_suffix = 'Error',
                        page_img_src = '/static/icon.svg',
                        page_headline = 'Error',
                        page_message = errors)
        
# no-edge
@app.route("/toss-coin/no-edge/<int:toss_quantity>/", methods=["GET"])
def toss_coin_no_edge_page(toss_quantity):
  
    if toss_quantity not in range(1,1001):
      return render_template('message.html',
                             page_title_suffix = ' - Error',
                             page_img_src = '/static/icon.svg',
                             page_headline = 'Invalid toss count',
                             page_message = 'Please enter a number between 1 and 1000.')
  
    else:
        coin_toss = toss_coin(toss_quantity,allow_edge=False)
        
        return render_template("roll.html",
                               page_toss_count = toss_quantity,
                               page_toss_list = coin_toss[RAW_TOSSES],
                               page_heads_count = coin_toss[HEADS_TOTAL],
                               page_tails_count = coin_toss[TAILS_TOTAL],
                               timestamp = get_timestamp(),
                               roll_type = 'heads-tails-coin-toss')
      
# with-edge
@app.route("/toss-coin/with-edge/<int:toss_quantity>/", methods=["GET"])
def toss_coin_with_edge_page(toss_quantity):
  
    if toss_quantity not in range(1,1001):
      return render_template('message.html',
                             page_title_suffix = ' - Error',
                             page_img_src = '/static/icon.svg',
                             page_headline = 'Invalid toss count',
                             page_message = 'Please enter a number between 1 and 1000.')
  
    else:
        coin_toss = toss_coin(toss_quantity,allow_edge=True)
        
        return render_template("roll.html",
                               page_toss_count = toss_quantity,
                               page_toss_list = coin_toss[RAW_TOSSES],
                               page_heads_count = coin_toss[HEADS_TOTAL],
                               page_tails_count = coin_toss[TAILS_TOTAL],
                               page_edge_count = coin_toss[EDGE_TOTAL],
                               timestamp = get_timestamp(),
                               roll_type = 'heads-tails-edge-coin-toss')
          
# magic 8 ball 2
@app.route("/magic-8-ball-v2/", methods=["GET"])
def magic_8_ball_page_2():

    message = shake_8_ball()

    return render_template("roll.html",
                           page_message = message,
                           timestamp = get_timestamp(),
                           roll_type = 'magic-8-ball-v2')
  
# roll functions
def roll_dice(dice_quantity=1, dice_type=6):
    """Generates a random number from 1 to x, y times
    PARAMETERS:
        dice_quantity:  INT
        dice_type:      number of faces on dice
    RETURNS:
        rolls:          set of integers
        roll_total:     INT
    """
    rolls = []
    roll_total = 0
    for _ in range(dice_quantity):
        roll = random.randint(1,dice_type)
        rolls.append(roll)
        roll_total += roll
    return [ rolls, roll_total ]

def toss_coin(toss_quantity=1, allow_edge=False):
    """Generates a random number between 0 (heads) and 1 (tails), toss_quantity times
        https://ui.adsabs.harvard.edu/abs/1993PhRvE..48.2547M/abstract
        "Extrapolations based on the model suggest that the probability of an American nickel landing on edge is approximately 1 in 6000 tosses."
    PARAMETERS:
        toss_quantity:  INT
        allow_edge:     BOOL
    RETURNS:
        tosses:         set of integers
        heads:          INT
        tails:          INT
        edge:           INT
        """
    tosses = []
    heads = 0
    tails = 0
    edge = 0

    if not allow_edge:
        for _ in range(toss_quantity):
            toss = random.randint(0,1)
            if toss == 0:
                tosses.append("heads")
                heads += 1
            elif toss == 1:
                tosses.append("tails")
                tails += 1

        return [ tosses, heads, tails ]

    else:
        for _ in range(toss_quantity):
            toss = random.randint(0,6000)
            if toss in range(1,3000):
                heads += 1
                tosses.append("heads")
            elif toss in range(3001,6000):
                tails += 1
                tosses.append("tails")
            elif toss == 0:
                edge += 1
                tosses.append("edge")

        return [ tosses, heads, tails, edge ]

def shake_8_ball():
    """Returns a random Magic 8 Ball message
    PARAMETERS:
        none
    RETURNS:
        message:    string
    """
    messages = [ "It is Certain.", 
            "It is decidedly so.",
            "Without a doubt.",
            "Yes definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.", ]
    
    message = random.choice(messages)
    message = message.upper()
    return message

def generate_numbers(number_min=0, number_max=100, number_qty=1, allow_dupes=False, sort=None, add_commas=True):
    """Generate random numbers
    PARAMETERS:
        number_min:     INT
        number_max:     INT
        number_qty:     INT
        allow_dupes:    BOOL
        sort:           None, "<" or ">"
    RETURNS:
        a set of strings
    """
    class RNGError(Exception):
        pass
    
    numbers = []

    if allow_dupes == False and (number_max - number_min) < number_qty:
        raise RNGError
    if number_max < number_min:
        raise RNGError
    for _ in range(number_qty):
        while True:
            number = random.randint(number_min,number_max)

            if not allow_dupes:
                if number in numbers:
                    continue
                else:
                    numbers.append(number)
                    break

            else:
                numbers.append(number)
                break

    if sort in ["ascending", "<", "small-to-large", "lowest-to-highest" ]:
        numbers.sort()

    elif sort in ["descending", ">", "large-to-small", "highest-to-lowest" ]:
        numbers.sort(reverse=True)

    if add_commas == True:
        number_strings = []

        for i in numbers:
            number_string = ('{:,}'.format(i))
            number_strings.append(number_string)

        return number_strings

    else:
        return numbers

def check_errors(number_min, number_max, number_qty, allow_dupes):
    """Check to prevent errors
    PARAMETERS:
        number_min:     INT
        number_max:     INT
        number_qty:     INT
        allow_dupes:    BOOL
        sort:           None, "<" or ">"
    RETURNS:
        a list of errors
    """
    errors = ""
    if allow_dupes == False and (number_max - number_min) < number_qty:
        errors = "ERROR: Requested quantity is greater than possible values. Broaden range or allow duplication."
    if number_max < number_min:
        errors = errors + "\n" + "ERROR: Minimum number is greater than maximum."
    if errors == "":
        return None
    else:
        return errors

def get_timestamp():
    return f'{datetime.now():%Y-%m-%d %H:%M:%S%z}'

def extract_fqdn(url):
  url = url.split("/")
  return url[2]

if __name__ == "__main__":
  app.run()