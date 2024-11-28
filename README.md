# Tottenham Stadium Events

An application designed to provide an easy-to-use solution for gathering all upcoming events at the Spurs Stadium, including concerts, rugby games, and football matches. Built to help non-tech-savvy users stay informed without navigating complex websites or multiple sources.

### Project Overview
This project was inspired by a real-world problem: a family member unfamiliar with English and technology struggled to find event schedules for the Spurs Stadium. To address this, I built an automated system that collects and displays all events hosted at the stadium in one place.

### How It Works
- Web scraping with Selenium: The app uses automation to extract event information from relevant sources, as there wasn’t a comprehensive free API available.
- Use of API: The app does leverage one free API for concert data. However, since the API occasionally includes duplicate events (i.e., events already processed via web scraping), the application includes logic to clean and filter the data for accuracy.
- User-focused design: The app focuses on simplicity and accessibility, making it ideal for users with minimal technical skills.

### Technologies Used
- Python/Django: Backend framework for building the server-side logic and handling data.

- React: Frontend framework for creating a user-friendly interface.

- Selenium: For web scraping and automated data extraction.

- API Integration: Concert data API used for fetching supplementary event information.

### Challenges and Solutions
- Limited APIs: Free APIs didn’t cover all types of events (concerts, rugby, etc.), so I implemented Selenium-based scraping to gather the necessary data.

- Ethical scraping: Implemented rate-limiting and other ethical practices to ensure scraping minimizes impact on the source websites.

### Ethical Considerations
This project adheres to ethical web scraping guidelines:

- Scrapes publicly available data.

- Operates with rate limits to reduce server strain.

- Intended strictly for personal and educational purposes, not for commercial use.


### Next Steps and Future Improvements
- API integration: Explore paid APIs for a more robust and scalable solution.

- Improved hosting: Migrate to a paid hosting service for better performance and reliability.

### User Impact
This project bridges a gap for users who might struggle with language or technology barriers, providing them with an easy way to access essential information. It demonstrates problem-solving, resourcefulness, and a commitment to creating user-focused solutions.

# Screenshots
### User is unable to refresh
To operate within rate limits, the user is forced to wait until the next possible refresh time is reached.

![Screenshot_46](https://github.com/user-attachments/assets/1d4aa510-f0ed-4c2b-8f80-bac27bfccf6d)

### User is able to refresh
Now that the time has been reached, user is able to refresh if they wish to.

![Screenshot_47](https://github.com/user-attachments/assets/8a1e628e-6c02-4e46-ae9a-9fe2aacb8c4f)
