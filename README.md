# Rollbot 🎲

Welcome to **Rollbot**, your versatile tabletop dice rolling companion for Discord! Whether you're embarking on epic adventures or engaging in strategic battles, Rollbot ensures your dice rolls are seamless and fair.

Deploy yourself or use the [publicly hosted version](https://discord.com/oauth2/authorize?client_id=712234733542572063&scope=bot&permissions=35840). Go to [the rollbot website](https://tmiedema.com/rollbot) for more information.

## Features ✨

- **Flexible dice rolling:** Supports standard and custom dice notations, including complex expressions like `d8+3` or `max(d20, d20) + 8`.
- **Probability distributions:** Visualize roll distributions to understand outcome probabilities.
- **User-friendly commands:** Intuitive slash commands for effortless interaction.
- **Macro management:** Create and manage roll macros for quick access to frequently used rolls.

## Usage 📖

Once RollBot is running, use the following commands in your Discord server:

- `/roll [expression]`: Rolls dice based on the provided expression.
- `/distribution [expression]`: Displays the probability distribution for the given roll expression.
- `/list`: Lists your saved roll macros.

### Examples of Roll Expressions

- **Basic Rolls:**
  - `d20`: Roll a 20-sided die.
  - `8d8`: Roll eight 8-sided dice.

- **Keep Highest Rolls:**
  - `3d20k2`: Roll three 20-sided dice and keep the highest two.
  - `4d6k3`: Roll four 6-sided dice and keep the highest three.

- **Math Operations:**
  - `d20 + 5`: Roll a 20-sided die and add 5.
  - `2d10 - 3`: Roll two 10-sided dice and subtract 3.

- **Logical Operations:**
  - `d20 > 15`: Roll a 20-sided die and check if the result is greater than 15.
  - `2d6 == 7`: Roll two 6-sided dice and check if the sum equals 7.

- **Functions:**
  - `max(d20, d12)`: Roll a 20-sided die and a 12-sided die, and take the maximum.
  - `min(d10, d8)`: Roll a 10-sided die and an 8-sided die, and take the minimum.
  - `fac(5)`: Compute the factorial of 5.
  - `comb(5, 2)`: Compute the combination of 5 choose 2.
  - `any(d6-3, d6-3, d6-3)`: Roll three 6-sided dice and return 1 if any result is greater than 0.

- **Assignments:**
  - `a = 2d20`: Assign the result of rolling two 20-sided dice to variable `a`.
  - `b = d8 + 3`: Assign the result of rolling an 8-sided die plus 3 to variable `b`.
  - `a &= 2d20`: Compute the result of rolling two 20-sided dice and assign it to variable `a`.

- **Multi-Rolls:**
  - `d20; d20 + 7`: Roll a 20-sided die, then roll another 20-sided die and add 7.
  - `reroll_1s_d6 = (d6; a &= (a == 1) * d6 + (a > 1) * a; a)`: Roll a 6-sided die, and if the result is 1, reroll it.

- **Comments:**
  - `"This is a roll:" d20; "And another one" d100 + 20`: Add comments to your roll expressions.

## Contributing 🤝

We welcome contributions! To get started:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m 'Add YourFeature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a pull request.

## License 📄

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements 🙏

Special thanks to all contributors and the open-source community for their invaluable support.
