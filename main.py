'''
Ardèche
'''
import mysql.connector
import os, sys, random, time, threading, winsound
import csv

import pyfiglet
from tabulate import tabulate
from gtts import gTTS

os.system('title Ardèche')

functions = ['Info', 'Practice', 'Zen', 'Add A Deck', 'Delete A Deck', 'Statistics', 'Settings', 'Exit']
sounds = {
    'Ding': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sounds\Ding.wav'),
    'Wrong Buzzer': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sounds\Wrong Buzzer.wav'),
}

positiveResponses = ['Nicely done!', 'Well done!', 'Good job!', 'Excellent!', 'Wonderful!', 'Amazing work!', 'Fantastic!', 'Great!']
negativeResponses = ['Sorry, but that is incorrect...', 'Oops, that\'s the wrong answer...', 'Try again next time...', 'Oh no...', 'Too bad, that\'s incorrect...']

print(pyfiglet.figlet_format("a r d ~ c h e", font="rishit"), end="")
print(tabulate([['Welcome to the flashcards app, Ardèche! Here, you can practice the language of French \nusing pre-created decks of flashcards, or even build your own!']], tablefmt='fancy_grid'), end="")

# Establishes connnection with MySQL Server
conn = mysql.connector.connect(
  host='localhost',
  user='admin', # assk for it
  password='password', # ask for it
  charset='utf8'
)

cursor = conn.cursor()

# Initialisation
try:
    # Tries to use use daatabase
    cursor.execute('use ardèche;')
except:
    # Creates and formulates database
    cursor.execute('create database ardèche;')
    cursor.execute('ALTER DATABASE ardèche CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
    cursor.execute("set names utf8;")

    cursor.execute('use ardèche;')

    # Creates default_deck
    cursor.execute('create table default_deck (ID integer PRIMARY KEY NOT NULL AUTO_INCREMENT, French_Word varchar(255), English_Word varchar(255), Mastery integer);')
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default.csv'), encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            frWord = f'\'{row[0]}\''
            enWord = f'\'{row[1]}\''
            cursor.execute(f'insert into default_deck (French_Word, English_Word, Mastery) values ({frWord}, {enWord}, 0);')
    conn.commit()

    # Establishes '_settings' table
    cursor.execute('create table _settings (ID integer PRIMARY KEY NOT NULL AUTO_INCREMENT, Setting varchar(255), Value varchar(255), AllPossibleValues varchar(255));')
    cursor.execute('insert into _settings (Setting, Value, AllPossibleValues) values (\'Language_Mode\', \'French\', \'French;English\'), (\'Theme\', \'Classic Dark-07\', \'Classic Dark-07;Classic Light-70;Hackerman-0a;Banana-e0;Clouds-9f;Cosmos-05;Calcium-f8\'), (\'Zen_Music\', \'Eternal Garden\', \'(None);Eternal Garden;Nebular Focus;Sunrise in Paris\');')
    conn.commit()

# Setting theme
cursor.execute('select Value from _settings where Setting = \'Theme\';')
theme = cursor.fetchall()[0][0].split("-")[1]
os.system(f'color {theme}')

# Choosing a deck
def chooseDeck():
    # Gathers all existing decks
    cursor.execute('show tables;')
    print(tabulate([['\nThe following decks are available:\n']], tablefmt='pretty'))
    decks = []
    for deck in cursor.fetchall():
        if not deck[0] == '_settings':
            decks.append(deck[0].replace('_', ' '))
    for deck in decks:
        print(f'\t[{decks.index(deck)+1}] {deck.title()}')

    # Makes user select a deck
    selected = False
    while not selected:
        selectedDeck = input('\n>> ')
        if selectedDeck.isnumeric() and (int(selectedDeck)-1) < len(decks):
            selectedDeck = decks[int(selectedDeck)-1]
            selected = True
        elif selectedDeck.lower() in decks:
            selected = True
        else:
            print('Sorry, that deck doesn\'t seem to exist. Please try again.')
    selectedDeck = selectedDeck.replace(' ', '_')
    print()

    global mode
    cursor.execute('select Value from _settings where Setting = \'Language_Mode\';')
    mode = cursor.fetchall()[0][0]

    return selectedDeck

# Using a deck
def useDeck():
    print(tabulate([['Practice']], tablefmt='fancy_grid'))
    print(tabulate([['Welcome to Practice mode! Here, you can practice the default deck, or the decks that you have created! \nAll progress made here will affect your statistics, where you can analyse words where you are strong or weak. \n(Remember to add the definite article before the nouns in French, \nand to add the \'to\' before the verbs in English!) Happy practicing!']], tablefmt='pretty'))
    selectedDeck = chooseDeck()

    # Selects the 25 questions
    questions = []
    cursor.execute(f'select * from {selectedDeck} order by Mastery asc, rand() limit 25;')
    for question in cursor.fetchall():
        questions.append(question)

    # Asks the questions
    if mode == 'French': # French-to-English
        correctAnswers = 0
        for question in questions:
            print(tabulate([[f'[{questions.index(question)+1}/25] What does the word \"{question[1].split(";")[0]}\" mean?']], tablefmt='pretty'))
            userAnswer = input('> ')

            if userAnswer.lower() in question[2].split(";"):
                print(tabulate([[f'{random.choice(positiveResponses)}']], tablefmt='fancy_grid'))
                print()
                winsound.PlaySound(sounds['Ding'], winsound.SND_FILENAME|winsound.SND_ASYNC)
                cursor.execute(f'update {selectedDeck} set Mastery = Mastery + 1 where ID = {question[0]};')
                conn.commit()
                correctAnswers += 1
            else:
                print(tabulate([[f'{random.choice(negativeResponses)} The correct answer was \"{question[2].split(";")[0]}\".']], tablefmt='fancy_grid'))
                print()
                winsound.PlaySound(sounds['Wrong Buzzer'], winsound.SND_FILENAME|winsound.SND_ASYNC)
                cursor.execute(f'update {selectedDeck} set Mastery = Mastery - 1 where ID = {question[0]};')
                conn.commit()
        print(tabulate([[f'The quiz has now ended. You scored {correctAnswers} out of 25!']], tablefmt='pretty'))
    elif mode == 'English': # English-to-French
        correctAnswers = 0
        for question in questions:
            print(tabulate([[f'({questions.index(question)+1}/25) What does the word \"{question[2].split(";")[0]}\" mean?']], tablefmt='pretty'))
            userAnswer = input('> ')

            if userAnswer.lower() in question[1].split(";"):
                print(tabulate([[f'{random.choice(positiveResponses)}']], tablefmt='fancy_grid'))
                print()
                winsound.PlaySound(sounds['Ding'], winsound.SND_FILENAME|winsound.SND_ASYNC)
                cursor.execute(f'update {selectedDeck} set Mastery = Mastery + 1 where ID = {question[0]};')
                conn.commit()
                correctAnswers += 1
            else:
                print(tabulate([[f'{random.choice(negativeResponses)} The correct answer was \"{question[1].split(";")[0]}\".']], tablefmt='fancy_grid'))
                print()
                winsound.PlaySound(sounds['Wrong Buzzer'], winsound.SND_FILENAME|winsound.SND_ASYNC)
                cursor.execute(f'update {selectedDeck} set Mastery = Mastery - 1 where ID = {question[0]};')
                conn.commit()
        print(tabulate([[f'The quiz has now ended. You scored {correctAnswers} out of 25!']], tablefmt='pretty'))
    else:
        print(tabulate([['An error has occurred. Please restart the program.']], tablefmt='pretty'))

# Adding a deck - WIP
def addDeck():
    deckCreated = False

    while not deckCreated:
        print(tabulate([['Enter the name of the deck you would like to create:']], tablefmt='fancy_grid'))
        deckName = input('>> ')
        deckName = deckName.lower()

        try:
            cursor.execute(f'create table {deckName.replace(" ", "_")} (ID integer PRIMARY KEY NOT NULL AUTO_INCREMENT, French_Word varchar(255), English_Word varchar(255), Mastery integer);')
        except:
            print('The name you entered was invalid. Please enter a different name.')
        else:
            deckCreated = True

# Deleting a deck
def deleteDeck():
    selectedDeck = chooseDeck()

    confirmation = ''
    while not confirmation == 'y':
        confirmation = input(f'Are you sure you want to delete {selectedDeck}? (y/n) ')
        if confirmation == 'n':
            break
        elif not confirmation == 'y':
            print('Sorry, that was invalid. Please enter again.')

    if confirmation == 'y':
        cursor.execute(f'drop table {selectedDeck}')

# WIP
def info():
    print(tabulate([['Information']], tablefmt='fancy_grid'))
    print(tabulate([['Ardèche is a department in southeast France known for its forests and trails. Even though\nit is a small part of France, it has vast and diverse geographical regions,\nlike mountains, plateaus, valleys, and its namesake, the Ardèche river.\n\nLearning a language, especially French, is a lot like Ardèche. There are high points, the mountains,\nwhere everything just clicks, and nothing is too difficult to conquer. Then, there are your plateaus,\nwhere everything just stagnates for a while, repetitive and monotonous. Then come the low points, valleys,\nwhich, inevitably, send you in a deep spiral where you question everything you do,\nfrom questions like "Why am I even learning this?" to "What even is oatmeal?". But then, comes the river.\nKind and gentle, the river flows along peacefully, minding its own business.\nIt has a sense of calmness and serenity, reassuring you of your knowledge,\nand that now, everything is going to be okay.\n\nBut throughout it all, you are surrounded by densely populated forests,\nsheltering and comforting you from the bad times, and nurturing you during the good.\nThrough thick and thin, you will always be protected by the forest.\nWelcome to Ardèche, I hope you have a good time.']], tablefmt='pretty'))

    time.sleep(29.5)

# WIP
def stats():
    print('Your strongest words are:')
    cursor.execute(f'select French_Word from default_deck order by Mastery desc limit 5;')
    counter = 1
    for word in cursor.fetchall():
        print(f'[{counter}] {word[0]}')
        counter += 1

    print('Your weakest words are:')
    cursor.execute(f'select French_Word from default_deck order by Mastery asc limit 5;')
    counter = 1
    for word in cursor.fetchall():
        print(f'[{counter}] {word[0]}')
        counter += 1

# Zen mode
def zen():
    # Zen music
    cursor.execute('select Value from _settings where Setting = \'Zen_Music\';')
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'sounds\zen\{cursor.fetchall()[0][0]}.wav')
    winsound.PlaySound(filePath, winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_LOOP|winsound.SND_NODEFAULT)

    print(tabulate([['Zen']], tablefmt='fancy_grid'))
    print(tabulate([['Welcome to Zen mode! In Zen mode, you can practice your decks without the hassles of your scores \nbeing recorded in your statistics! No record will be stored, but you will still get to practice \nALL of the questions in one particular deck!']], tablefmt='pretty'))
    selectedDeck = chooseDeck()

    # Selects the questions
    questions = []
    cursor.execute(f'select * from {selectedDeck} order by Mastery asc, rand();')
    for question in cursor.fetchall():
        questions.append(question)

    cursor.execute(f'select COUNT(*) from {selectedDeck}')
    total = cursor.fetchall()[0][0]

    # Asks the questions
    if mode == 'French': # French-to-English
        correctAnswers = 0
        for question in questions:
            print(tabulate([[f'[{questions.index(question)+1}/{total}] What does the word \"{question[1].split(";")[0]}\" mean?']], tablefmt='pretty'))
            userAnswer = input('> ')

            if userAnswer.lower() in question[2].split(";"):
                print(tabulate([[f'{random.choice(positiveResponses)}']], tablefmt='fancy_grid'))
                print()
                correctAnswers += 1
            else:
                print(tabulate([[f'{random.choice(negativeResponses)} The correct answer was \"{question[2].split(";")[0]}\".']], tablefmt='fancy_grid'))
                print()
        print(tabulate([[f'The quiz has now ended. You scored {correctAnswers} out of {total}!']], tablefmt='pretty'))
    elif mode == 'English': # English-to-French
        correctAnswers = 0
        for question in questions:
            print(tabulate([[f'({questions.index(question)+1}/{total}) What does the word \"{question[2].split(";")[0]}\" mean?']], tablefmt='pretty'))
            userAnswer = input('> ')

            if userAnswer.lower() in question[1].split(";"):
                print(tabulate([[f'{random.choice(positiveResponses)}']], tablefmt='fancy_grid'))
                print()
                correctAnswers += 1
            else:
                print(tabulate([[f'{random.choice(negativeResponses)} The correct answer was \"{question[1].split(";")[0]}\".']], tablefmt='fancy_grid'))
                print()
        print(tabulate([[f'The quiz has now ended. You scored {correctAnswers} out of {total}!']], tablefmt='pretty'))
    else:
        print(tabulate([['An error has occurred. Please restart the program.']], tablefmt='pretty'))
    winsound.PlaySound(None, winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_LOOP|winsound.SND_NODEFAULT)

# WIP (reset button mayhaps => init func() and make sure to call at ACTUAL init aswell)
def settings():
    print(tabulate([['Settings']], tablefmt='fancy_grid'))
    print(tabulate([['Here, you can change the mode of the app. Please choose the language in which you would like your flashcards to be:']], tablefmt='pretty'))
    print()

    # Gathers settings
    settings = []
    cursor.execute('select Setting from _settings;')
    for setting in cursor.fetchall():
        settings.append(setting[0].replace("_", " "))
    for setting in settings:
        print(f'\t[{settings.index(setting)+1}] {setting.title()}')

    # Makes user select a setting
    selected = False
    while not selected:
        editSetting = input('\n>> ')
        if editSetting.isnumeric() and (int(editSetting)-1) < len(settings):
            editSetting = settings[int(editSetting)-1]
            selected = True
        elif editSetting.title() in settings:
            selected = True
        else:
            print('Sorry, that setting doesn\'t seem to exist. Please try again.')
    editSetting = editSetting.title()
    print()

    # Sets the language mode of the app
    def langMode():
        # Gathers existing modes
        cursor.execute('select AllPossibleValues from _settings where Setting = \'Language_Mode\';')
        options = cursor.fetchall()[0][0].split(";")
        for option in options:
            print(f'\t[{options.index(option)+1}] {option.title()}')

        # Makes user select a mode
        selected = False
        while not selected:
            selectedMode = input('\n>> ')
            if selectedMode.isnumeric() and (int(selectedMode)-1) < len(options):
                selectedMode = options[int(selectedMode)-1]
                selected = True
            elif selectedMode.lower() in options:
                selected = True
            else:
                print('Sorry, that mode doesn\'t seem to exist. Please try again.')
        selectedMode = selectedMode.title()

        cursor.execute(f'update _settings set Value = \'{selectedMode}\' where Setting = \'Language_Mode\';')
        conn.commit() #

        print(tabulate([[f'The mode of the app has now been set to \'{selectedMode}\'.']], tablefmt='fancy_grid'))
        print()

    # Changes the theme
    def themeChange():
        # Gathers existing themes
        cursor.execute('select AllPossibleValues from _settings where Setting = \'Theme\';')
        themes = {}
        for themeOption in cursor.fetchall()[0][0].split(";"):
            themes[themeOption.split("-")[0]] = themeOption.split("-")[1]
        index = 1
        for themeOption in themes:
            print(f'\t[{index}] {themeOption}')
            index += 1

        # Makes user select a theme
        selected = False
        while not selected:
            selectedTheme = input('\n>> ')
            if selectedTheme.isnumeric() and (int(selectedTheme)-1) < len(themes):
                selectedTheme = list(themes.keys())[int(selectedTheme)-1] # Working with dictionaries is tiresome
                selected = True
            elif any([var for var in themes if var == selectedTheme.title()]):
                selectedTheme = [var for var in themes if var == selectedTheme.title()][0]
                selected = True
            else:
                print('Sorry, that theme doesn\'t seem to exist. Please try again.')
        os.system(f'color {themes[selectedTheme]}')

        cursor.execute(f'update _settings set Value = \'{selectedTheme+"-"+themes[selectedTheme]}\' where Setting = \'Theme\';')
        conn.commit()

        print(tabulate([[f'The theme of the app has now been set to \'{selectedTheme}\'.']], tablefmt='fancy_grid'))
        print()

    # Changes the music playing in Zen mode
    def zenMusicChange():
        # Gathers existing options
        cursor.execute('select AllPossibleValues from _settings where Setting = \'Zen_Music\';')
        songs = []
        for songOption in cursor.fetchall()[0][0].split(";"):
            songs.append(songOption)
        for songOption in songs:
            print(f'\t[{songs.index(songOption)+1}] {songOption}')

        # Makes user select a theme
        selected = False
        while not selected:
            selectedSong = input('\n>> ')
            if selectedSong.isnumeric() and (int(selectedSong)-1) < len(songs):
                selectedSong =  songs[int(selectedSong)-1]
                selected = True
            elif any([var for var in songs if var.lower() == selectedSong.lower()]):
                selectedSong = [var for var in songs if var.lower() == selectedSong.lower()][0]
                selected = True
            else:
                print('Sorry, that song doesn\'t seem to exist. Please try again.')

        cursor.execute(f'update _settings set Value = \'{selectedSong}\' where Setting = \'Zen_Music\';')
        conn.commit()

        print(tabulate([[f'The song of the Zen mode has now been set to \'{selectedSong}\'.']], tablefmt='fancy_grid'))
        print()

    if editSetting == settings[0]:
        langMode()
    elif editSetting == settings[1]:
        themeChange()
    elif editSetting == settings[2]:
        zenMusicChange()

# Main Loop
while True:
    time.sleep(0.5)
    print('\n')
    print(tabulate([['Select any one of the following functions, either by typing their name, corresponding number!']], tablefmt='pretty'))
    print('\n')
    for function in functions:
        print(f'\t[{functions.index(function)+1}] {function}')
    action = input('\n\n>>  ')
    print('\n')

    if action.isnumeric() and (int(action)-1) < len(functions):
        chosenFunc = functions[int(action)-1]
    elif action.title() in functions:
        chosenFunc = action.title()
    else:
        print(tabulate([['Sorry, that function doesn\'t seem to exist. Please try again.']], tablefmt='pretty'))
        continue

    if chosenFunc == 'Info':
        info()
    elif chosenFunc == 'Practice':
        useDeck()
    elif chosenFunc == 'Zen':
        zen()
    elif chosenFunc == 'Add A Deck':
        addDeck()
    elif chosenFunc == 'Delete A Deck':
        deleteDeck()
    elif chosenFunc == 'Statistics':
        stats()
    elif chosenFunc == 'Settings':
        settings()
    elif chosenFunc == 'Exit':
        print(tabulate([['Have a nice day!']], tablefmt='fancy_grid'))
        sys.exit()
