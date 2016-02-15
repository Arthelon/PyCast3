#!/usr/bin/python
import os, re
from clint.textui import puts, prompt, validators, progress
import requests, feedparser


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def geturl(url, dst):
    if os.path.isfile(dst):
        halt_exec = prompt.options("A file already exists with that name. Continue?", options=[
            {'selector': 'Y', 'prompt': 'yes', 'return': False},
            {'selector': 'N', 'prompt': 'no', 'return': True}
        ])
        if halt_exec:
            raise SystemExit('Move the file and try again')
    try:
        req = requests.get(url, stream=True)
        req.raise_for_status()
    except requests.exceptions.HTTPError:
        raise SystemExit(
            "There was an error retrieving the data. Check your internet connection and try again."
        )
    with open(dst, "wb") as f:
        total_length = req.headers.get('content-length')

        if total_length is None: # no content length header
            f.write(req.content)
        else:
            total_length = int(total_length)
            for chunk in progress.bar(req.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()


def get_data(link, json=True):
    try:
        req = requests.get(link)
        req.raise_for_status()
    except requests.exceptions.HTTPError:
        raise SystemExit(
            "There was an error retrieving the data. Check your internet connection and try again."
        )
    if json:
        return req.json()
    return req.content


def main():
    while True:
        podcast_search = prompt.query("Podcast you want to download: ")
        clear()
        podcast_search = re.sub(r" ", "+", podcast_search)
        url = "https://itunes.apple.com/search?term=" + podcast_search + "&entity=podcast"
        data = get_data(url)
        result_count = int(data["resultCount"])
        if result_count <= 0:
            puts('No results found, please search again')
            continue
        puts("{:d} results were found. Displaying the top ten now".format(result_count))
        for i in range(result_count):
            puts("{:d}: {:s}".format(
                i + 1,
                data["results"][i]["trackName"]
            ))
            if len(data["results"][i]["artistName"]) > 40:
                data["results"][i]["artistName"] = data["results"][i]["artistName"][0:40]+'...'
            puts("\tArtist: {:s}".format(
                data["results"][i]["artistName"]
            ))
            puts()
        user_selection = int(prompt.query("Enter podcast number (0 if None): ", validators=[
            validators.IntegerValidator()
        ]))
        clear()
        if user_selection == 0:
            raise SystemExit('Goodbye!')
        elif 0 < user_selection <= result_count:
            podcast_name = data["results"][user_selection - 1]["trackName"]
            podcast_id = data["results"][user_selection - 1]["collectionId"]
            puts("You have selected {:s}".format(podcast_name))
            break
        else:
            puts("Incorrect number, please search again.")
    url = "https://itunes.apple.com/lookup?id=" + str(podcast_id) + "&entity=podcast"
    data = get_data(url)
    rss_url = data["results"][0]["feedUrl"]
    data_root = feedparser.parse(get_data(rss_url, json=False))['entries']

    enclosures = [entry.enclosures[0].href for entry in data_root]
    titles = [entry.title for entry in data_root]
    ext = re.search(r'\.\w+?$', enclosures[0]).group(0)

    mp3list = []
    for link in enclosures:
        mp3list.append(link)

    num_titles = len(titles)

    puts("{:d} titles found, printing the latest 10...".format(num_titles))

    for i in range(min(10, len(titles))):
        puts('[{:d}] {:s}'.format(i+1, titles[i].strip('\n')))
    puts()

    download_all = False
    download_one = -1
    download_new = False;
    download_range_start = -1
    download_range_finish = -1
    bad_input = True

    while bad_input:
        bad_input = False
        if bad_input:
            puts('Error: bad input')
        user_download = prompt.options('Select download options ', options=[
            'All',
            'Latest',
            'Specific file',
            'Range'
        ])
        clear()
        if user_download == 1:
            download_all = True
        elif user_download == 2:
            download_new = True
        elif user_download == 3:
            user_download = prompt.query('Enter file number', validators=[
                validators.IntegerValidator()
            ])
            clear()
            if 0 < user_download < 11:
                download_one = len(mp3list) - int(user_download) + 1
            else:
                bad_input = True
                continue
        else:
            user_download = prompt.query('Enter file range (ex: 1 - 3)')
            clear()
            if '-' in user_download:
                try:
                    range_list = [int(num.strip()) for num in user_download.split('-')]
                except ValueError:
                    bad_input = True
                    continue
                download_range_start = len(mp3list) - int(range_list[1])
                download_range_finish = len(mp3list) - int(range_list[0])
                if len(range_list) != 2 or not (0 < download_range_start <
                                                    download_range_finish < 11):
                    bad_input = True
                    continue
            else:
                bad_input = True
                continue
        break
    base_path = os.path.dirname(os.path.realpath(__file__))
    if download_all:
        for i in range(len(mp3list)):
            puts("Downloading: {:s}".format(titles[i]))
            save_loc = "{:s}/{:s}{:s}".format(
                base_path,
                titles[i],
                ext
            )
            geturl(mp3list[i], save_loc)
            puts()
    elif download_one >= 0:
        puts("Downloading: {:s}".format(titles[int(download_one)]))
        save_loc = "{:s}/{:s}{:s}".format(
            base_path, titles[int(download_one)], ext
        )
        geturl(mp3list[int(download_one)], save_loc)
    elif download_new:
        puts("Downloading: {:s}".format(titles[0]))
        save_loc = "{:s}/{:s}{:s}".format(
             base_path,
             titles[0],
             ext
        )
        geturl(mp3list[int(download_one)], save_loc)
    else:
        for i in range(download_range_start, download_range_finish + 1):
            puts("Downloading: {:s}".format(titles[i]))
            save_loc = "{:s}/{:s}{:s}".format(
                base_path,
                titles[i],
                ext
            )
            geturl(mp3list[i], save_loc)
            puts()
    puts('Process Complete')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        puts('\nStopped by keyboard interrupt')
