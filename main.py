from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# Initialize Selenium WebDriver
def init_driver(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)  # Adjust the wait time as needed
    return driver


# Accept cookies
def accept_cookies(driver):
    try:
        accept_button = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
        accept_button.click()
        print("Cookies accepted.")
    except Exception as e:
        print("Error accepting cookies:", e)


# Toggle leaders based on user input
def toggle_leader_type(driver, leader_choice):
    wait = WebDriverWait(driver, 10)
    try:
        if leader_choice == 'season':
            season_leaders_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='SEASON LEADERS']")))
            season_leaders_button.click()
            print("Switched to Season Leaders.")
        elif leader_choice == 'yesterday':
            print("Defaulted to Yesterday's Leaders.")
        else:
            print("Invalid choice. Exiting.")
            driver.quit()
            exit()
        time.sleep(2)
    except Exception as e:
        print("Failed to toggle between leaders:", e)
        driver.quit()
        exit()


# Extract player data
def extract_player_data(soup):
    titles = [title.text for title in soup.find_all('h2', class_='LeaderBoardCard_lbcTitle___WI9J')][:9]
    rows = soup.select("table.LeaderBoardPlayerCard_lbpcTable__q3iZD tbody tr")
    player_data = []
    for row in rows[:45]:
        rank_cell = row.find("td", class_="LeaderBoardPlayerCard_lbpcTableCell__SnM1o")
        player_name_cell = row.find("a", class_="LeaderBoardPlayerCard_lbpcTableLink__MDNgL")
        team_cell = row.find("span", class_="LeaderBoardPlayerCard_lbpcTeamAbbr__fGlx3")
        score_cell = row.find("td", class_="LeaderBoardWithButtons_lbwbCardValue__5LctQ")
        player_data.append({
            "Rank": rank_cell.get_text(strip=True).rstrip('.') if rank_cell else "N/A",
            "Player": player_name_cell.get_text(strip=True) if player_name_cell else "N/A",
            "Team": team_cell.get_text(strip=True) if team_cell else "N/A",
            "Score": score_cell.get_text(strip=True) if score_cell else "N/A"
        })
    return titles, player_data


# Extract team data
def extract_team_data(soup):
    titles = [title.text for title in soup.find_all('h2', class_='LeaderBoardCard_lbcTitle___WI9J')][9:]
    rows = soup.select("table.LeaderBoadTeamCard_lbtcTable__gmmZz tbody tr")
    team_data = []
    for row in rows:
        rank_cell = row.find("td", class_="LeaderBoadTeamCard_lbtcTableCell__RJFMA")
        team_name_cell = row.find("a", class_="LeaderBoadTeamCard_lbtcTableLink__LyoJz")
        score_cell = row.find("td", class_="LeaderBoardWithButtons_lbwbCardValue__5LctQ")
        team_data.append({
            "Rank": rank_cell.get_text(strip=True).rstrip('.') if rank_cell else "N/A",
            "Team": team_name_cell.get_text(strip=True) if team_name_cell else "N/A",
            "Score": score_cell.get_text(strip=True) if score_cell else "N/A"
        })
    return titles, team_data


# Save data to CSV
def save_to_csv(data, titles, choice, leader_choice):
    today = datetime.now().strftime("%Y-%m-%d")
    csv_filename = f"nba_{choice}_stats_{leader_choice}_{today}.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Title', 'Rank', choice.capitalize(), 'Score']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for i, title in enumerate(titles):
            start = i * 5
            end = start + 5
            for item in data[start:end]:
                writer.writerow({
                    'Title': title,
                    'Rank': item['Rank'],
                    choice.capitalize(): item.get(choice.capitalize(), "N/A"),
                    'Score': item['Score']
                })
    print(f"{choice.capitalize()} stats saved to {csv_filename}.")


# Main function to run the scraper
def main():
    url = "https://www.nba.com/stats"
    driver = init_driver(url)
    accept_cookies(driver)

    # User selection
    leader_choice = input("Retrieve Yesterday's or Season Leaders? (yesterday/season): ").strip().lower()
    toggle_leader_type(driver, leader_choice)

    # Get page source and close driver
    page_source = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_source, "html.parser")

    # User selection for player/team stats if yesterday is chosen
    if leader_choice != 'season':
        choice = input("Retrieve Player or Team Stats? (player/team): ").strip().lower()
    else:
        choice = 'player'

    # Extract and save data based on choice
    if choice == 'player':
        titles, data = extract_player_data(soup)
        save_to_csv(data, titles, "player", leader_choice)
    elif choice == 'team':
        titles, data = extract_team_data(soup)
        save_to_csv(data, titles, "team", leader_choice)
    else:
        print("Invalid choice. Please enter 'player' or 'team'.")


if __name__ == "__main__":
    main()
