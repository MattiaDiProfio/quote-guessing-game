"""
Quote Guessing Game
Mattia Di Profio
22/05/2023

Project Description : 
- The following project was a great opportunity to revise the python syntax as well 
  as getting hands-on experience with the web-scraping framework BeautifulSoup
- The code below works by scraping quotes from a website with scraping-permissions, 
  and formats the contents into a guessing game with the user.
- I tried to keep the code efficient by saving the data to a csv file when fetched, 
  by doing so we only need to scrape once, keeping the code efficient.
"""

from bs4 import BeautifulSoup
import requests
from csv import reader, writer
from random import choice


def scrape_page(page_num = 1):
    """
    returns a list whose first entry determines if the last scrapable page has been reached
    and whose other entries are tuples in the form (quote, author, author birth data)
    """

    #obtain and parse html data 
    res = requests.get(f'http://quotes.toscrape.com/page/{page_num}/')
    res_html = res.text
    soup = BeautifulSoup(res_html, "html.parser")
    page_data = []

    #check that next button exists on current page
    next_btn = soup.select(".next")
    next_link = False if not len(next_btn) else True
    page_data.append(next_link)

    #extract and format the required quote data from the current page
    quote_divs = soup.select(".quote")  
    for quote in quote_divs:
        text = quote.select(".text")[0].get_text()
        author_name = quote.select(".author")[0].get_text()
        
        #to exract author birthplace and birthdate we need to navigate to a different link
        #which follows the format 'http://quotes.toscrape.com/author/{author-name}/'
        author_info_link = quote.select(".author")[0].find_next('a')['href']
        aux_res = requests.get(f'http://quotes.toscrape.com{author_info_link}')

        #create a soup object on the author's 'about' page for further parsing
        author_soup = BeautifulSoup(aux_res.text, "html.parser")
        birth_place = author_soup.select(".author-born-location")[0].get_text()
        birth_date = author_soup.select(".author-born-date")[0].get_text()
        author_birth_data = f'Author was born {birth_place} on {birth_date}.'

        quote_data = (text, author_name, author_birth_data)
        page_data.append(quote_data)

    return page_data

def initials(s):
    """
    auxiliary function to extract the initals from an author's name
    """
    letters = [x for x in list(s) if x in "QWERTYUIOPASDFGHJKLZXCVBNM"]
    return f"Author's initials are {letters[0]}. {letters[1]}."


def play_game(quotes_list, play=True):
    """
    recursive function that implements the functionality of each round in the game
    """
    #previous function call stops execution by setting 'play' control variable to false
    if not play:
        print("Thanks for playing the game, goodbye!")
        return None
    
    #choose and unpack a quote-tuple at random from the larger collection, passed as an argument
    quote_data = choice(quotes_list)
    text, name, birth_data = list(quote_data)
    hints = [birth_data, initials(name)] #create 2 hints for the user
    guesses_left = 2

    print("I got a quote for you : ", text)
    guess = str(input("Your goal is to guess who wrote this quote. Enter your guess here : "))

    while guess != name and guesses_left:
        print(f"You have {guesses_left} guesses left.")
        if len(hints): #print hints only if hints list is non-empty
            print("Wrong guess! Here's a hint : ", hints.pop())
            guess = str(input("Your goal is to guess who wrote this quote. Enter your guess here : "))
        guesses_left -= 1

    #determine whether while loop terminated due to user's victory or loss
    if not guesses_left:
        print("You lost :(. The quote was authored by ", name)
    else:
        print("Well done! You guessed right!")

    #obtain and validate user's prompt to play again or stop playing
    play_again = str(input("Would you like to play again? (y/n) : "))
    while play_again not in "yn":
        print("Invalid command, please enter 'y' or 'n'.")
        play_again = str(input("Would you like to play again? (y/n) : "))

    #function calls itself, with equal quotes list and updated control variable
    return play_game(quotes_list, True) if play_again == "y" else play_game(quotes_list, False)


if __name__ == "__main__":
    #program checks if quotes have already been scraped and saved to csv file
    try:
        #code here executes if YES, encoding kwarg allows for broader UNICODE chars comprehension
        with open("scraped_quotes.txt", encoding='UTF-8') as f:
            f_reader = reader(f)
            #read each row to a tuple and build list of quote-tuples
            global_data = [tuple(row) for row in f_reader if row]
        
        play_game(global_data)

    except FileNotFoundError:
        #code here executes if quotes have not been scraped before
        page_num = 1
        global_data = []
        continue_scraping = True

        #loop scrapes current page and advances to next one until possible
        #'global_data' list gradually contains more quotes as scraping proceeds 
        #at the time of execution, 100 quotes are found
        while continue_scraping:
            curr_page_data = scrape_page(page_num)
            global_data += curr_page_data[1:]
            continue_scraping = curr_page_data[0]
            page_num += 1

        #write freshly-scraped data to a csv file to speed-up future executions.
        with open("scraped_quotes.txt", "w", encoding='UTF-8') as f:
            f_writer = writer(f)
            headers = ['quote contents', 'author name', 'author birth details']
            f_writer.writerow(headers)
            for row in global_data:
                f_writer.writerow(row)
            
        play_game(global_data)

