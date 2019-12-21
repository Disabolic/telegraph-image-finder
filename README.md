### Image search from telegraph
___
The main purpose of this script is to find and download available pictures from articles in the telegraph. The idea for this script is based on the telegraph linking rule for new articles.
Usually it looks like:
```
https://telegra.ph/Example-article-12-21
https://telegra.ph/Example-article-12-21-2
```
or
```
https://telegra.ph/tag-date[-number]
```

| Option | Description |
| ------ | ----------- |
| tag    | title for your article, tag, tag-tag, etc. |
| date   | month and day of article creation, -month-day. |
|[number]| article number, if it was created on the same day with the same title, -number. Only for number > 1. |

Below is an example of running a script with optional arguments:
```
python main.py [tag] [number_of_threads_for_search] [number_of_threads_for_download]
```
or
```
python main.py travel
```
If the images for this tag were found, a folder will be created inside the download folder with the tag name and available images will be loaded into it.
