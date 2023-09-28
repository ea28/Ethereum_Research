import requests
from bs4 import BeautifulSoup
from csv import writer
from collections import Counter
import pandas as pd
import re

# Function to perform scraping and write data to CSV
def scrape_and_write_data(output_file):
    with open(output_file, "w", encoding='utf-8', newline="") as f:
        writer_obj = writer(f)
        header = ["Title", "Website", "Category", "Author", "Article Body", "Comments", "Comment Authors"]
        writer_obj.writerow(header)

        NUMBER_OF_PAGES = 70  # there are 70 pages
        for num in range(NUMBER_OF_PAGES):
            URL = 'https://ethereum-magicians.org/?page=' + str(num)
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")
            topics = soup.find_all('span', class_='link-top-line')
            for topic in topics:
                info = extract_info_from_topic(topic)
                writer_obj.writerow(info)


def extract_info_from_topic(topic):
    title = topic.text.replace("\n", '')
    topic_url = topic.find('a')['href']
    info = [title, topic_url]

    subpage = requests.get(topic_url)
    subpage_soup = BeautifulSoup(subpage.content, "html.parser")

    category = subpage_soup.find("span", itemprop="name").text.replace("\n", '')
    username = subpage_soup.find("span", itemprop="author").text.replace("\n", '')
    article_body = subpage_soup.find("div", itemprop="articleBody").text.replace("\n", '')

    comments_html = subpage_soup.find_all('div', class_='post')
    comments = "".join(comment.text.replace("\n", '') + "##$$##" for comment in comments_html[1:])

    comment_authors = subpage_soup.find_all("span", itemprop="author")[1:]
    list_of_authors = [author.find('span', itemprop="name").text for author in comment_authors]
    comment_author_count_cleaned = str(Counter(list_of_authors))[9:-2]

    info.extend([category, username, article_body, comments, comment_author_count_cleaned])
    return info


def update_dataframe(input_file, output_file):
    df = pd.read_csv(input_file)
    pattern = re.compile(r'\b(?:EIP|ERC)[ -]?(\d+)', re.IGNORECASE)

    def extract_number(text):
        match = pattern.search(text)
        return int(match.group(1)) if match else None

    df['EIP'] = df['Title'].apply(extract_number).astype('Int64')
    df = df[['EIP'] + [col for col in df if col != 'EIP']]
    df.to_csv(output_file, index=False)


def filter_dataframe(input_file, eips_file, output_file):
    ethereum_magicians_df = pd.read_csv(input_file)
    all_eips_df = pd.read_csv(eips_file)

    ethereum_magicians_df = ethereum_magicians_df.dropna(subset=['EIP'])
    ethereum_magicians_df['EIP'] = ethereum_magicians_df['EIP'].astype(int)
    filtered_df = ethereum_magicians_df[ethereum_magicians_df['EIP'].isin(all_eips_df['EIP_Number'])]
    filtered_df.to_csv(output_file, index=False)


if __name__ == "__main__":
    temp_file = "ethereum_magicians.csv"
    updated_file = "ethereum_magicians_updated.csv"
    final_file = "ethereum_magicians_filtered.csv"
    all_eips_file = "AllEIPs.csv"

    scrape_and_write_data(temp_file)
    update_dataframe(temp_file, updated_file)
    filter_dataframe(updated_file, all_eips_file, final_file)
