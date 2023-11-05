# ComBot 🤖

Welcome to **ComBot**, your all-in-one solution for managing communities with ease! This bot is equipped with a variety of features to enhance your community management experience. From user information retrieval to games, anime suggestions, and utility functions, this bot has got you covered.


## Getting Started 🛠️

1. **Clone the repository:**
   ```
   git clone https://github.com/New-dev0/combot.git
   cd combot
   ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Configure the bot:**
   - Create a Bot App on Switch and obtain the API token.
   - Create `.env` file, similar to [.env.sample](./.env.sample)

4. **Create a firebase database**
   - Fill the `FIREBASE_URL` in `.env` and `SERVICE_ACCOUNT_FILE` to the path of service account (.json).

5. **Run the bot:**
   ```
   python3 bot.py
   ```

## Contributions 🤝

Contributions are welcome! If you have any suggestions or find issues, please open an issue or create a pull request.

## License 📝

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
